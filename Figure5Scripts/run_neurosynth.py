## File for running neurosynth and saving to a directory

from brainstat.context.meta_analysis import meta_analytic_decoder
import numpy as np
import nibabel as nib
import ssl
import urllib.request
import argparse
import sys, os


def loadVolume(lh_path, rh_path):
    lh_data = nib.load(lh_path).agg_data()
    rh_data = nib.load(rh_path).agg_data()
    arr = np.concatenate((lh_data, rh_data))
    return arr


def thresholdArr(arr, threshQuantile):
    ## Get the absolute value
    absArr = np.abs(arr)
    ## Get the threshold values
    threshPos = np.percentile(absArr, int(threshQuantile))
    threshNeg = threshPos * -1
    print(f"Threshold for Positive Values: {threshPos}")
    print(f"Threshold for Negative Values: {threshNeg}")
    ## Threshold the data
    threshArrPos = np.where(
        arr < threshPos,
        0,
        arr,
    )
    threshArrNeg = np.abs(np.where(arr > threshNeg, 0, arr))
    return threshArrNeg, threshArrPos


def getCorr(arr):
    ssl._create_default_https_context = ssl._create_unverified_context
    meta = meta_analytic_decoder(
        "fslr32k",
        arr,
        data_dir=f"{os.getcwd()}/data/external/neurosynth-data-master",
    )
    meta["index"] = meta.index
    return meta


def filterTerms(meta):
    labels = [
        "face/affective processing",
        "affective",
        "verbal",
        "semantics",
        "verbal semantics",
        "attention",
        "working memory",
        "autobiographical memory",
        "episodic memory",
        "semantic memory",
        "recognition memory",
        "reading",
        "inhibition",
        "motor",
        "visual perception",
        "visual attention",
        "cognitive control",
        "social cognition",
        "cognitive impairment",
        "cognitive functions",
        "word recognition",
        "reward",
        "decision making",
        "multisensory",
        "visuospatial",
        "eye movements",
        "action",
        "auditory",
        "pain",
        "language",
        "emotion",
        "visual stream",
    ]
    meta_vis = meta[np.isin(meta["index"], labels)]
    return meta_vis


def saveSurf(threshNeg, threshPos, output):
    if not os.path.exists(output):
        os.mkdir(output)
    lh_gii_neg = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(data=threshNeg[: threshNeg.shape[0] // 2])]
    )
    rh_gii_neg = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(data=threshNeg[threshNeg.shape[0] // 2 :])]
    )
    lh_gii_pos = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(data=threshPos[: threshPos.shape[0] // 2])]
    )
    rh_gii_pos = nib.gifti.GiftiImage(
        darrays=[nib.gifti.GiftiDataArray(data=threshNeg[threshPos.shape[0] // 2 :])]
    )
    nib.save(lh_gii_neg, os.path.join(output, "lh_negative_thresh.func.gii"))
    nib.save(rh_gii_neg, os.path.join(output, "rh_negative_thresh.func.gii"))
    nib.save(lh_gii_pos, os.path.join(output, "lh_positive_thresh.func.gii"))
    nib.save(rh_gii_pos, os.path.join(output, "rh_positive_thresh.func.gii"))


def saveData(metaThresh, meta, type, output):
    if not os.path.exists(output):
        os.mkdir(output)
    metaThresh.to_csv(os.path.join(output, f"{type}.terms.filtered.csv"), index=False)
    meta.to_csv(os.path.join(output, f"{type}.terms.csv"), index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lh", help="Path for left hemisphere surface")
    parser.add_argument("--rh", help="Path for right hemisphere surface")
    parser.add_argument("--threshold", required=False)
    parser.add_argument(
        "--output",
        help="Directory to save outuput to (will be created if does not exist)",
    )
    args = parser.parse_args()
    arr = loadVolume(args.lh, args.rh)
    if args.threshold is None:
        print("Threshold not supplied, running global analysis")
        meta = getCorr(arr)
        metaFilt = filterTerms(meta)
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        meta.to_csv(os.path.join(args.output, "terms.csv"), index=False)
        metaFilt.to_csv(os.path.join(args.output, "terms.filtered.csv"), index=False)
        return
    threshArrNeg, threshArrPos = thresholdArr(arr, args.threshold)
    saveSurf(threshArrNeg, threshArrPos, args.output)
    if not np.all(threshArrNeg == 0):
        metaNeg = getCorr(threshArrNeg)
        metaNeg = metaNeg[metaNeg["Pearson's r"] > 0]
        metaNegFilter = filterTerms(metaNeg)
        saveData(metaNegFilter, metaNeg, "negative", args.output)
    if not np.all(threshArrPos == 0):
        metaPos = getCorr(threshArrPos)
        metaPos = metaPos[metaPos["Pearson's r"] > 0]
        metaPosFilter = filterTerms(metaPos)
        saveData(metaPosFilter, metaPos, "positive", args.output)


if __name__ == "__main__":
    main()
