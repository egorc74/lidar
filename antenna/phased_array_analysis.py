from variables import *
import os
from scipy.signal import czt, zoom_fft

def main(sim):
    if os.path.exists("data/single_antenna_data.npz"):
            
            c_0=3e8
            data = np.load("data/single_antenna_data.npz")
            E2_air_corrected = data["E2_air_corrected"]
            ux_air = data["ux_air"]
            uy_air = data["uy_air"]
            f = data["f"]
            ux_peak_fit=data["ux_peak_fit"]
            wavelengths = c_0/f
    else:
        print("ERROR:extract data in data_extaction.py first")
        return None
        
#####################################################################  
# File: phased_array_analysis.lsf
#
# Description: This file loads the angular distribution data created by
# LIDAR2_analysis.lsf and then does an analysis of a phased antenna
# array. The user can choose a target polar angle (theta) and azimuthal
# angle (phi) and the script will attempt to steer the beam in that 
# direction by using a linear phase. The user can also adjust the
# weight function.
######################################################################   
# user settings
######################################################################  
    theta_target = 20 # in degrees
    phi_target = 30 # in degrees
    n = 48 # number of antenna elements
    pitch = 1.6e-6 # phased array pitch
    y=np.linspace(-(n-1)/2,(n-1)/2,n)*pitch
    dB_range = 40 # max range for viewing angular distributions
    # uncomment the appropriate amplitude weight function, or create your own
    #amplitude_weight = 1 # uniform
    amplitude_weight = np.exp( -y**2/(10*pitch)**2 ) # gaussian std=10*pitch/sqrt(2)
######################################################################  


# ######################################################################   
# # phased array calculation
# ######################################################################  
    ux_target = np.sin(theta_target*np.pi/180)*np.cos(phi_target*np.pi/180)
    uy_target = np.sin(theta_target*np.pi/180)*np.sin(phi_target*np.pi/180)
    # Limit ranges
    if ux_target<np.min(ux_peak_fit) and ux_target > np.max(ux_peak_fit):
        print(f"cannot hit ux at this angle. Min pheta: {180/np.pi*np.min(ux_peak_fit)}")
        print(f"Max pheta: {180/np.pi*np.max(ux_peak_fit)}")
        return None
    f_index=np.argmin(np.abs(ux_target-ux_peak_fit))
    k0 = 2*np.pi*f[f_index]/c_0
    weight = amplitude_weight*np.exp(-1j*k0*uy_target*y)    #phase_correction=exp(-1j* k_steering * R) 
    weight_ft2 = abs(sim.czt( weight,y,k0*uy_air))**2 # FT of weight functio n
    plot(Num_v=1,x=k0*uy_air,variables=[weight_ft2],x_label="K directions, on y arc",labels=["czt"],y_label="magnitude squared",graph_label="czt of weight")
    Ux_air,Weight_ft=np.meshgrid(ux_air,weight_ft2)
    print(Weight_ft.shape)
    print(E2_air_corrected.shape)
    print(f_index)
    print(weight_ft2)

    E2_steered = (E2_air_corrected[:,:,f_index]*Weight_ft.T)
    colorplot(x=ux_air,y=uy_air,F=np.abs(Weight_ft),x_label="ux_air",y_label="uy_air",graph_tiltle=f"Beam stearing for theta: {theta_target} and phi: {phi_target} ")
    
    E2_final=E2_steered/np.max(E2_steered)
    colorplot(x=ux_air,y=uy_air,F=np.abs(E2_air_corrected[:,:,f_index]),x_label="ux_air",y_label="uy_air",graph_tiltle=f"Beam stearing for theta: {theta_target} and phi: {phi_target} ")
    colorplot(x=ux_air,y=uy_air,F=np.abs(E2_final),x_label="ux_air",y_label="uy_air",graph_tiltle=f"Beam stearing for theta: {theta_target} and phi: {phi_target} ")

if __name__=="__main__":
    main(lumapi.FDTD(filename_fdtd))








