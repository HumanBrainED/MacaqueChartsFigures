## File will take in paths to gradients to align
import argparse
from brainspace.gradient import GradientMaps
from brainspace.mesh.mesh_io import read_surface
from brainspace.plotting import plot_hemispheres
from brainspace.utils.parcellation import map_to_labels
import numpy as np
import nibabel as nb
import glob
import sys, os


def get_parcellations(parcellation):
    # Takes in parcellation type and returns numpy data array for lh and rh from label.gii file
    if parcellation == "markov":
        lh_markov = nb.load(
            "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/L.MarkovCC12_M132_91-area.32k_fs_LR.label.gii"
        )
        lh_markov_data = lh_markov.agg_data()

    return lh_markov_data


def loadGradients(args):
    ## Need to load the data and save stack them in a numpy array?
    pc1_pattern = os.path.join(args.folder, "*PC1.csv")
    pc2_pattern = os.path.join(args.folder, "*PC2.csv")
    pc1_file_list = glob.glob(pc1_pattern)
    pc2_file_list = glob.glob(pc2_pattern)
    pc1_file_names = [
        os.path.splitext(os.path.basename(file))[0] for file in pc1_file_list
    ]
    pc2_file_names = [
        os.path.splitext(os.path.basename(file))[0] for file in pc2_file_list
    ]
    pc1_data = []
    pc2_data = []
    for file in pc1_file_list:
        data = np.loadtxt(file, delimiter=",")
        pc1_data.append(data)
    pc1_data = np.transpose(np.array(pc1_data))
    for file in pc2_file_list:
        data = np.loadtxt(file, delimiter=",")
        pc2_data.append(data)
    pc2_data = np.transpose(np.array(pc2_data))
    return pc1_data, pc2_data


def alignGradients(pc1_data, pc2_data, alignment):
    ## Convert the matrix to squares
    num_rows = 91
    pc1_gp = GradientMaps(kernel="normalized_angle", alignment="procrustes")
    pc1_matrix_list = []
    for col in range(pc1_data.shape[1]):
        pc1_vector = pc1_data[1:, col]
        pc1_matrix = np.tile(pc1_vector, (91, 1)).T
        pc1_matrix_list.append(pc1_matrix)
    pc1_gp.fit(pc1_matrix_list)
    # pc2_gp = GradientMaps(kernel="normalized_angle", alignment="procrustes")
    # pc2_matrix_list = []
    # for col in range(pc2_data.shape[1]):
    #    pc2_vector = pc2_data[1:col]
    #    pc2_matrix = np.tile(pc2_vector, (91, 1)).T
    #    pc2_matrix_list.append(pc2_matrix)
    # pc2_gp.fit(pc2_matrix_list)
    return pc1_gp


def visualizeSurface(pc1_gp, label_data, folder):
    lh_surf = read_surface(
        "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/MacaqueYerkes19.L.inflated.32k_fs_LR.surf.gii"
    )
    rh_surf = read_surface(
        "/Users/Sam.Alldritt/Documents/CMI/PRIME-DE/BrainChartsCode/PRIME-DE-Lifespan/Atlas/markov/MacaqueYerkes19.R.inflated.32k_fs_LR.surf.gii"
    )
    pc1_aligned = [None] * 6
    pc2_aligned = []
    for i in range(6):
        lh_data = map_to_labels(np.insert(pc1_gp.aligned_[i][:, 0], 0, 0), label_data)
        rh_data = map_to_labels(np.insert(pc1_gp.aligned_[i][:, 0], 0, 0), label_data)
        data = np.vstack((lh_data, rh_data))
        pc1_aligned[i] = np.reshape(data, (-1))
        # pc2_aligned[i] = map_to_labels(pc2_gp.aligned_[i], label_data)
    label_text = ["0-0.33yrs", "0.33-1yrs", "1-2yrs", "2-6yrs", "6-15yrs", "15-25yrs"]
    pc1_filename = os.path.join(folder, "pc1_aligned.png")
    plot_hemispheres(
        lh_surf,
        rh_surf,
        array_name=pc1_aligned,
        size=(1200, 400),
        cmap="coolwarm",
        color_bar=True,
        label_text=label_text,
        filename=pc1_filename,
        zoom=1.5,
        interactive=False,
        screenshot=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", help="Path to folder with gradients to align")
    parser.add_argument("--alignment", choices=["procrustes", "joint"])
    args = parser.parse_args()

    parcellation = get_parcellations("markov")
    pc1_data, pc2_data = loadGradients(args)
    pc1_gp = alignGradients(pc1_data, pc2_data, args.alignment)
    visualizeSurface(pc1_gp, parcellation, args.folder)


if __name__ == "__main__":
    main()
