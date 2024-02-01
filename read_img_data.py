import h5py
import numpy as np
import matplotlib.pyplot as plt


data_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_01_31_15h44m52s_OL_multistep_TEST"

img_folder = "/OL_data_0/thermal_images"
Niter = 1000
plt.ion()
for i in range(Niter):
    with h5py.File(data_folder+img_folder+f"/iter{i}.h5", 'r') as f:
        img_data = np.asarray(f['image'])

    plt.imshow(img_data)
    plt.title(f"Iteration {i}")
    plt.pause(0.1)
    plt.clf()
