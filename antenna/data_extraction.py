from variables import *    
from scipy.interpolate import RegularGridInterpolator
import os
import decimal
from scipy.interpolate import interp1d
import pandas as pd

def fourier_farfield(sim):  
    # mname = "top_m"
    mname = "top_m"
######################################################################   
# plot transmission into glass superstrate
######################################################################  
    farfield_resolution = 300
    sim.farfieldfilter(0.1) # see https://kb.lumerical.com/en/index.html?ref_scripts_farfieldfilter.html
 

    c_0=3e8
    if os.path.exists("data/farfield_data.npz"):
        data = np.load("data/farfield_data.npz")
        E2 = data["E2"]
        ux = data["ux"]
        uy = data["uy"]
        f = data["f"]
        wavelengths = c_0/f

    else:
        f = sim.getdata(mname,"f").flatten()
        E2 = sim.farfield3d(mname,np.linspace(1,len(f),len(f)),farfield_resolution,farfield_resolution)
        E2=np.nan_to_num(E2, nan=0)
        ux = sim.farfieldux(mname,1,farfield_resolution,farfield_resolution).flatten()
        ux=np.nan_to_num(ux, nan=0)
        uy = sim.farfielduy(mname,1,farfield_resolution,farfield_resolution).flatten()
        uy=np.nan_to_num(uy, nan=0)
        wavelengths = c_0/f
        np.savez("data/farfield_data", E2=E2, ux=ux, uy=uy, f=f)



 

######################################################################   

######################################################################   
# image angle in air vs wavelength
######################################################################  
    n_glass = 1.444
    angle=np.arcsin(ux*n_glass)*180/np.pi
    angle=np.nan_to_num(angle, nan=0)
    F=E2[:,int(len(uy)/2),:]


    # colorplot(x=angle,y=wavelengths,F=F.T,x_label="angles",y_label="wavelengths",graph_tiltle="Farfield in air")
    

    if os.path.exists("data/nearfield_data.npz"):
        data = np.load("data/nearfield_data.npz")    
        E_x = data["E_x"]
        E_y = data["E_y"]
        E_z = data["E_z"]
        x = data["x"]
        y = data["y"]

    else:
        
        E_x = sim.getdata(mname,"Ex")
        E_y = sim.getdata(mname,"Ey")
        E_z = sim.getdata(mname,"Ez")

        E_x = E_x[:,:,0,:]
        E_y = E_y[:,:,0,:]
        E_z = E_z[:,:,0,:]
            
        x = sim.getdata(mname,"x")[:,0]
        y = sim.getdata(mname,"y")[:,0]
        np.savez("data/nearfield_data", E_x=E_x, E_y=E_y, E_z=E_z, x=x, y=y)

    magnitude_E=np.sqrt((np.abs(E_x)**2+np.abs(E_y)**2+np.abs(E_z)**2))

    print(np.diff(x)[0])
    print(np.diff(x)[500])


    Arg_E_x=np.angle(E_x)
    Arg_E_y=np.angle(E_y)
    Arg_E_z=np.angle(E_z)
 

    k0=2*np.pi/wavelengths
 

# Choose a padding factor (2x, 4x, etc.)
    Nx, Ny = magnitude_E[:,:,0].shape
    pad_factor = 5

    # Compute new shape
    Nx_pad = Nx * pad_factor
    Ny_pad = Ny * pad_factor

    # Pad symmetrically with zeros

    # U0=magnitude_E*np.exp(-1j*(Arg_E_x+Arg_E_y))
    U0=E_x*E_y/np.abs(E_x)/np.abs(E_y)*magnitude_E
    U0_padded = np.pad(U0[:,:,1],
                    (((Nx_pad - Nx)//2, (Nx_pad - Nx)//2),
                    ((Ny_pad - Ny)//2, (Ny_pad - Ny)//2)),
                    mode='constant', constant_values=0)
    print(U0_padded.shape)


    ##FFT of U0
    fft_result = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(U0_padded)), axes=(0, 1))
    #fx and fy
    fx = np.fft.fftshift(np.fft.fftfreq(Nx_pad, d=np.diff(x)[0]))
    fy = np.fft.fftshift(np.fft.fftfreq(Ny_pad, d=np.diff(y)[0]))
    Fx, Fy = np.meshgrid(fx, fy, indexing='ij')

    inverse_fft_result=np.zeros_like(U0_padded)
    fft_result_propagated=np.zeros_like(fft_result)
    phase=np.zeros_like(Fx)
    wl=1.550e-6
    phase=2*np.pi*1*np.sqrt(1/wl**2-Fx**2-Fy**2 +0j)
    Im_phase=np.imag(phase) 
    count= np.sum((Im_phase > 1000) | (Im_phase < -1000))
          
    print(count)    
    H = np.zeros_like(phase)
    mask = (Im_phase > -1000) & (Im_phase < 1000)
    H[mask] = np.exp(1j*phase[mask])

    fft_result_propagated=fft_result*H

    inverse_fft_result = np.fft.ifft2(np.fft.ifftshift(fft_result_propagated), axes=(0, 1))
    inverse_fft_result = np.fft.ifftshift(inverse_fft_result, axes=(0, 1))
    del phase, H
    colorplot(x=x,y=y,F=np.abs(inverse_fft_result),x_label="x (um)",y_label="y (um)",graph_tiltle="Inverse FFT of U0")  





def get_decay_length(sim, plt=None):
    mname = "forward_m"
    mname = "waveguide_analysis::T1"
    
    T = sim.getresult(mname,"T")["T"]
    f=sim.getdata(mname,"f")
    Lx=l
    print(f"Length of the antenna:{Lx}")
    alpha=-np.log(T)/Lx
    L_dec=1/alpha   #decay lengths for all frequencies
    if plt!=None:
        plot(Num_v=1,x=f,variables=[L_dec],labels=["decay lengths"],x_label="frequencies",y_label="decay_lengths",graph_label="decay_lengths vs freq")
    return L_dec




def data_correction(sim):

    mname = "above"
######################################################################   
# plot transmission into glass superstrate
######################################################################  
    farfield_resolution = 401
    sim.farfieldfilter(0.1) # see https://kb.lumerical.com/en/index.html?ref_scripts_farfieldfilter.html
 

    c_0=3e8
    if os.path.exists("data/farfield_data.npz"):
        data = np.load("data/farfield_data.npz")
        E2 = data["E2"]
        ux = data["ux"]
        uy = data["uy"]
        f = data["f"]
        wavelengths = c_0/f

    else:
        f = sim.getdata(mname,"f").flatten()
        E2 = sim.farfield3d(mname,np.linspace(1,len(f),len(f)),farfield_resolution,farfield_resolution)
        E2=np.nan_to_num(E2, nan=0)
        ux = sim.farfieldux(mname,1,farfield_resolution,farfield_resolution).flatten()
        ux=np.nan_to_num(ux, nan=0)
        uy = sim.farfielduy(mname,1,farfield_resolution,farfield_resolution).flatten()
        uy=np.nan_to_num(uy, nan=0)
        wavelengths = c_0/f
        np.savez("data/farfield_data", E2=E2, ux=ux, uy=uy, f=f)

    n_glass = 1.444
    angle=np.arcsin(ux*n_glass)*180/np.pi
    angle=np.nan_to_num(angle, nan=0)


######################################
# Get nearfield
######################################
    '''
    if os.path.exists("data/nearfield_data.npz"):
        data = np.load("data/nearfield_data.npz")    
        E_x = data["E_x"]
        E_y = data["E_y"]
        E_z = data["E_z"]
        x = data["x"]
        y = data["y"]

    else:
        
        E_x = sim.getdata(mname,"Ex")
        E_y = sim.getdata(mname,"Ey")
        E_z = sim.getdata(mname,"Ez")

        E_x = E_x[:,:,0,:]
        E_y = E_y[:,:,0,:]
        E_z = E_z[:,:,0,:]
            
        x = sim.getdata(mname,"x")[:,0]
        y = sim.getdata(mname,"y")[:,0]
        np.savez("data/nearfield_data", E_x=E_x, E_y=E_y, E_z=E_z, x=x, y=y) 
 
    '''
################################ ######################################   
# calculate emission in air, accounting for refraction using Snell's law
######################################################################  
    # interpolate all frequencies to air
    interp_func = RegularGridInterpolator((ux*n_glass, uy*n_glass, f), E2, bounds_error=False, fill_value=0)
    ux_air = np.linspace(-1, 1, farfield_resolution)
    uy_air = np.linspace(-1,1,  farfield_resolution)
    
    

    # make the target grid
    UX_air  , UY_air, F_air = np.meshgrid(ux_air, uy_air, f, indexing='ij')
    points = np.stack([UX_air.ravel(), UY_air.ravel(), F_air.ravel()], axis=-1)
    E2_air = interp_func(points).reshape(UX_air.shape)
    colorplot(x=ux_air,y=uy_air,F=np.abs(E2_air[:,:,1]),x_label="ux air",y_label="uy air",graph_tiltle="interpolated far field")



######################################################################   

######################################################################   
# Correct for the finite simulation length (x span) and determine the ux of the peak emission vs frequency
######################################################################   
    L_dec = get_decay_length(sim=sim,plt=1)
    """Interpolate L_dec for smoother results"""
    k0 = 2*np.pi*f/c_0
    UX_air, UY_air, K0 = np.meshgrid(ux_air, uy_air, k0, indexing='ij')
    fwhm = 1.287/(k0*L_dec)    #2*sqrt(-1+sqrt(2))
    f_0=(np.min(f)+np.max(f))/2
    fwhm_coeffs = np.polyfit(f, fwhm, deg=2)
    fwhm_fit=fwhm_coeffs[0]*(f)**2+fwhm_coeffs[1]*(f)+fwhm_coeffs[2]
    plot(Num_v=2,x=f,variables=[fwhm_fit,fwhm],labels=["fwhm_fit","actual fwhm"],x_label="frequency",y_label="fwhm_fit",graph_label="fwhm vs frequency")

######################################################################                     
# Find ux that corresponds to peak in farfield (find peak in E2_air for each freq and find corresponding ux_air for it)
#####################################################################
    ux_peak_air = np.zeros(len(f))

    for i in range(len(f)):
        freq_slice=E2_air[:,:,i]
        indx=np.argmax(freq_slice)
        max_indices = np.unravel_index(indx,freq_slice.shape) #returns tuple of indexes
        ux_indx,uy_indx=max_indices
        ux_peak_air[i]=ux_air[ux_indx]
    ux_peak_coefs = np.polyfit(f-f_0, ux_peak_air, deg=2)   
    ux_peak_fit=ux_peak_coefs[0]*(f-f_0)**2+ux_peak_coefs[1]*(f-f_0)+ux_peak_coefs[2] 
    plot(Num_v=1,x=f-f_0,variables=[ux_peak_fit],labels=["ux_peak_fit"],x_label="frequency",y_label="ux_peak_fit",graph_label="peak Emission at ux vs frequency")


    """Now we have for each frequency angle of emmision and FWHM_x Lorentz distribution of fourier transform"""

    
    # fit ux_peak vs frequency with polynomial
    
    # apply finite length correction to the data

    alpha=1/L_dec
    a,Uy_Air,Ux_peak = np.meshgrid(ux_air,uy_air,ux_peak_fit)
    au,bu,ALPHA=np.meshgrid(ux_air,uy_air,alpha)

    """We need to correct our FARFIELD profile due to an error, which arises after truncation of our distribution """
    """We assume that at each wavelength an angular spread arrises on the x axis, and posses Lorentzian distribution. """
    """FWHM for angular distribution was calculated before [2/(Ldec*K0)] or 2*alpha/K0 """
    """So Lorentzian has shape 1/[(pheteta-pheta_0)**2 + (FWHM/2)**2], which is equal to K0**2/[K0**2*(pheta-pheta_0)**2 + alpha**2]"""
    """If we normalize this distribution we finaly get alpha**2/(K0**2*(pheta-pheta_0)**2-alpha**2)"""
    E2_air_corrected = E2_air*ALPHA**2/(K0**2 * (UX_air-Ux_peak)**2 +ALPHA**2 ) # correct for fact that simulation was not full length (Lorentzian due to exponential decay)
    colorplot(x=ux_air,y=uy_air,F=np.abs(E2_air_corrected[:,:,1]),x_label="x (um)",y_label="y (um)",graph_tiltle="Inverse FFT of U0")  
# ######################################################################  

# ######################################################################  
# # create data set for easier visualization of the angular distribution
######################################################################  

# ######################################################################  


# ####################################################################
# # create an unstructured data set using the script at https://kx.lumerical.com/t/creating-a-far-field-radiation-plot-from-fdtd-angular-distributions/23397
# ####################################################################
    Ux_air,Uy_air = np.meshgrid(ux_air,uy_air)
    Uz_air = np.real( np.sqrt(1-Ux_air**2-Uy_air**2 +0j) )
    nx = len(ux_air)
    ny = len(uy_air)
    nRect=(nx-1)*(ny-1)
    C=np.zeros((2*nRect,3),dtype=int)
    Uz_flat = Uz_air.ravel()


    # Find valid positions excluding max edges (rightmost and topmost points)
    _pos = np.where((Ux_air.ravel() != np.max(ux_air)) & (Uy_air.ravel() != np.max(uy_air)))
    pos=_pos[0]

    maskA = (Uz_flat[pos] > 0) | (Uz_flat[pos + 1] > 0) | (Uz_flat[pos + 1 + ny] > 0)
    posA = pos[maskA]

    # Fill first triangle set
    cPosA = np.arange(len(posA))
    C[cPosA, 0] = posA
    C[cPosA, 1] = posA + 1
    C[cPosA, 2] = posA + 1 + ny

    # Select positions for second triangle
    maskB = (Uz_flat[pos] > 0) | (Uz_flat[pos + ny] > 0) | (Uz_flat[pos + 1 + ny] > 0)
    posB = pos[maskB]

    # Fill second triangle set
    cPosB = len(posA) + np.arange(len(posB))
    C[cPosB, 0] = posB
    C[cPosB, 1] = posB + 1 + ny
    C[cPosB, 2] = posB + ny

    # Trim unused rows
    C = C[:len(posA) + len(posB), :]


    # pos = find( (Ux_air != max(ux_air)) & (Uy_air != max(uy_air)) )
    # posA = pos(find(Uz_air(pos) | Uz_air(pos+1) | Uz_air(pos+1+ny)))
    # cPos = 1:length(posA)
    # C(cPos,1) = posA
    # C(cPos,2) = posA+1
    # C(cPos,3) = posA+1+ny
    # posB = pos(find(Uz_air(pos) | Uz_air(pos+1+ny) | Uz_air(pos+ny)))
    # cPos = length(posA) + (1:length(posB))
    # C(cPos,1) = posB
    # C(cPos,2) = posB+1+ny
    # C(cPos,3) = posB+ny
    # C = C(1:(length(posA)+length(posB)),:)
    
    from matplotlib.tri import Triangulation

    
    E2_flat = E2_air_corrected.reshape(nx * ny, len(f))
    E2_dB_positive = 10 * np.log10(E2_flat)
    E2_dB_positive = E2_dB_positive - np.max(E2_dB_positive) + 60  # normalize to 60 dB range
    E2_dB_positive[E2_dB_positive < 0] = 0  # clip below 0 dB
    E2_slice=E2_dB_positive[:,1]

    tri = Triangulation(Ux_air.ravel(), Uy_air.ravel(), C)

    # === Convert to 3D coordinates on unit sphere ===
    X = Ux_air.ravel()
    Y = Uy_air.ravel()
    Z = Uz_air.ravel()

    # === 3D Visualization ===
    # fig = plt.figure(figsize=(7, 6))
    # ax = fig.add_subplot(111, projection='3d')

    # tpc = ax.plot_trisurf(X, Y, Z, triangles=C, cmap='jet',
    #                     linewidth=0.1, antialiased=True,
    #                     shade=False, facecolors=plt.cm.jet(E2_slice))

    # ax.set_xlabel('Ux')
    # ax.set_ylabel('Uy')
    # ax.set_zlabel('Uz')
    # ax.set_title('Far-field Intensity on 3D Sphere (dB)')
    # ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio
    # plt.tight_layout()
    # plt.show()

######################################################################
# Save data for phase array ananlysis
######################################################################
    np.savez("data/single_angtena_data", E2_air_corrected=E2_air_corrected, ux_air=ux_air, uy_air=uy_air, f=f,ux_peak_fit=ux_peak_fit)


if __name__ == "__main__":
    # data_correction(sim=lumapi.FDTD(filename_fdtd))
    filename_guide="C:/Users/egorc/FAKS_FE/LPVO/OPA_with_wg_antenna/lumerical_guide/LIDAR2.fsp"
    data_correction(sim=lumapi.FDTD(filename_guide))
    
