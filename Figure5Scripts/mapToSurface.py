## This file takes in a csv file of peak data and maps it onto a surface
# Needs peak data, label file, and surface

import numpy as np
import nibabel as nib
import argparse
import os


def create_gifti_with_metadata(data_array):
    gii = nib.gifti.gifti.GiftiImage()
    meta = nib.gifti.gifti.GiftiMetaData()
    gii.meta.data_type = "CIFTI-2"
    gii.meta.meta = meta
    data_array = data_array.astype(np.float32)
    data_array = nib.gifti.gifti.GiftiDataArray(data_array)
    gii.add_gifti_data_array(data_array)
    return gii


def mapData(parcellation, lh_path, rh_path):
    lh_peaks = np.genfromtxt(lh_path)
    rh_peaks = np.genfromtxt(rh_path)
    if parcellation == "markov":
        lh_label = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/L.MarkovCC12_M132_91-area.32k_fs_LR.label.gii"
        ).agg_data()
        rh_label = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/R.MarkovCC12_M132_91-area.32k_fs_LR.label.gii"
        ).agg_data()
        lh_surf = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/MacaqueYerkes19.L.inflated.32k_fs_LR.surf.gii"
        )
        rh_surf = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/MacaqueYerkes19.R.inflated.32k_fs_LR.surf.gii"
        )
    elif parcellation == "aparc":
        lh_label = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/aparc/fs_LR.aparc.L.32k.func.gii"
        ).agg_data()
        rh_label = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/aparc/fs_LR.aparc.L.32k.func.gii"
        ).agg_data()
        lh_surf = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/surfaces/human/32k_fs_LR/sub-MNI152NLin2009cAsym.L.midthickness.32k_fs_LR.surf.gii"
        )
        rh_surf = nib.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/surfaces/human/32k_fs_LR/sub-MNI152NLin2009cAsym.R.midthickness.32k_fs_LR.surf.gii"
        )
    lh_surf_vertices = lh_surf.darrays[0].data
    rh_surf_vertices = rh_surf.darrays[0].data
    ## Now remap the data
    lh_func_gii = nib.gifti.gifti.GiftiImage()
    lh_mapped = np.zeros(lh_surf_vertices.shape[0])
    rh_func_gii = nib.gifti.gifti.GiftiImage()
    rh_mapped = np.zeros(rh_surf_vertices.shape[0])
    for i, label in enumerate(lh_label):
        label = int(label)
        lh_mapped[i] = lh_peaks[label]
    for i, label in enumerate(rh_label):
        label = int(label)
        rh_mapped[i] = rh_peaks[label]
    lh_func_gii = create_gifti_with_metadata(lh_mapped)
    rh_func_gii = create_gifti_with_metadata(rh_mapped)
    return (lh_func_gii, rh_func_gii)


def saveData(lh_func, rh_func, savePrefix):
    nib.save(lh_func, f"{savePrefix}.lh.func.gii")
    nib.save(rh_func, f"{savePrefix}.rh.func.gii")


def main(args):
    lh_func, rh_func = mapData(args.parcellation, args.lh_csv, args.rh_csv)
    saveData(lh_func, rh_func, args.save_prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map peak data to surface space")
    parser.add_argument("--lh-csv", required=True)
    parser.add_argument("--rh-csv", required=True)
    parser.add_argument("--parcellation", required=True, choices=["markov", "aparc"])
    parser.add_argument("--save-prefix", required=True)
    args = parser.parse_args()
    main(args)
