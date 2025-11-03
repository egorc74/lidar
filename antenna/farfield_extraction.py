


import numpy as np
import matplotlib.pyplot as plt
from variables import *
from scipy.interpolate import RegularGridInterpolator


def plot_farfield(sim):
    sim.farfieldfilter(0.5)
    f = sim.getdata("top_m","f")
    E2 = sim.farfield3d("top_m",np.linspace(1,len(f),len(f)),501,1)
    E2 = np.abs(E2[:-1, 0, :])  
    E2_norm = (E2 - np.min(E2)) / (np.max(E2) - np.min(E2))
    ux = sim.farfieldux("top_m",1,501)
    ux=ux[:-1]
    UX=np.array(ux.flatten())
    F=np.array(f.flatten())
    print(F)
    print(UX)


    #interpolate function 
    interp_func = RegularGridInterpolator((UX, F), E2_norm)
    ux_new = np.linspace(UX.min(), UX.max(), 800)
    f_new = np.linspace(F.min(), F.max(), 400)


    UX_new, F_new = np.meshgrid(ux_new, f_new, indexing='ij')
    points = np.array([UX_new.ravel(), F_new.ravel()]).T

    # Interpolate
    E2_interp = interp_func(points).reshape(UX_new.shape)


    c_0=3e8
    wavelengths=c_0/f_new
    angles=np.arcsin(ux_new)*180/np.pi    

    plt.figure(figsize=(8,6))
    plt.pcolormesh(wavelengths, angles, np.log10(E2_interp), shading='auto', cmap='jet')
    plt.xlabel('Frequency f')
    plt.ylabel('ux')
    plt.title('Interpolated Far-Field Pattern')
    plt.colorbar(label='|E|² (normalized)')
    plt.show()
if __name__=="__main__":
    plot_farfield(lumapi.FDTD(filename_fdtd))