from variables import *
resolution=300


def far_field(sim,plot=None,f=1):
    m="top_m"
    data=sim.farfieldpolar3d(m,f,resolution,resolution)
    ux = sim.farfieldux(m,f,resolution,resolution); 
    uy = sim.farfielduy(m,f,resolution,resolution); 
    E_r=data[:,:,0]
    E_phe=data[:,:,1]
    E_phi=data[:,:,2]
    I=np.abs(E_r**2+E_phe**2+E_phi**2)      ## still ux uy dependent 
    phi=np.linspace(0,360,resolution)
    the=np.linspace(0,90,resolution)
    
    ## Second way
    E = sim.farfield3d(m,f,resolution,resolution); 
    theta_1=np.linspace(0,90,resolution)
    phi_1=np.linspace(0,360,resolution)
    Theta,Phi = np.meshgrid(theta_1,phi_1)
    E_sph=sim.farfieldspherical(E,ux,uy,Theta,Phi)
    print(E_sph.shape)
    E_sph = E_sph.reshape(resolution, resolution,order='F')
    

    if plot!=None:  
        plt.imshow(np.abs(E.T), extent = [np.min(ux), np.max(ux), np.min(uy), np.max(uy)], aspect = 'auto', origin = 'lower', cmap = 'jet')
        plt.xlabel('x (um)')
        plt.ylabel('y (um)')
        plt.colorbar()
        plt.show()

        plt.imshow(I.T, extent = [np.min(the), np.max(the), np.min(phi), np.max(phi)], aspect = 'auto', origin = 'lower', cmap = 'jet')
        plt.xlabel('phe ')
        plt.ylabel('phi ')
        plt.colorbar()
        plt.show()

        plt.imshow(E_sph, extent = [np.min(theta_1), np.max(theta_1), np.min(phi_1), np.max(phi_1)], aspect = 'auto', origin = 'lower', cmap = 'jet')
        plt.xlabel('the ')
        plt.ylabel('phi ')
        plt.colorbar()
        plt.show()
    return E_sph


def wavelength_angle_dep(sim):
    resolution=300
    m="top_m"
 
    for f in range(1,6):
         ## Second way

        E = sim.farfield3d(m,f,resolution,resolution); 
        ux = sim.farfieldux(m,f,resolution,resolution); 
        uy = sim.farfielduy(m,f,resolution,resolution); 
        theta_1=np.linspace(0,90,resolution)
        phi_1=np.linspace(0,360,resolution)
        Theta,Phi = np.meshgrid(theta_1,phi_1)
        E_sph=sim.farfieldspherical(E,ux,uy,Theta,Phi)
        E_sph = E_sph.reshape(resolution,resolution,order='F')
        plt.plot(theta_1*np.pi/180,E_sph[150,:], label=f'curve for 1 mm length')  # x in micrometers

    plt.xlabel("x (µm)")
    plt.ylabel("Value")
    plt.title("1 mm length antenna")
    #If you want the legend, uncomment below (but it may get messy with 51 labels):
    plt.legend()
    plt.show()







def calculate_field(distance,N_a,E0,betta):
    wavelength=1.550e-6
    k0=2*np.pi/wavelength
    theta=np.linspace(0,np.pi/2,resolution)
    phi=np.linspace(0,2*np.pi,resolution)
    Theta,Phi=np.meshgrid(theta,phi)
    AF=np.zeros_like(Phi,dtype=complex)
    phase=np.full(N_a,k0*distance*np.sin(betta))
    for m in range(N_a-1):
        a=m*(k0*distance*np.sin(Phi)*np.cos(Theta)+phase[m])
        AF+=np.exp(1j*a)        #try minus


    return E0*AF
    

def weight_vector(N_a,k_vector,distance,phi):
    W=[]
    for i in range(N_a):
        W.append(np.exp(1j*k_vector*i*distance*np.cos(phi)))
    return W

def steering_vector(N_a,k_vector,distance,phi):
    V=[]
    for i in range(N_a):
        V.append(np.exp(-1j*i*np*(k_vector*distance)))
    return V
def array_factor(W,V):
    AF=np.dot(W,V)
    return AF



def plot_field(E):
    the=np.linspace(0,90,resolution)
    phi=np.linspace(0,360,resolution)
    plt.imshow(np.abs(E**2), extent = [np.min(the), np.max(the), np.min(phi), np.max(phi)], aspect = 'auto', origin = 'lower', cmap = 'jet')
    plt.xlabel('the ')
    plt.ylabel('phi ')
    plt.colorbar()
    plt.show()


def phase_calculation(betta,wavelength,distance,degrees=None):
    k0=2*np.pi/wavelength
    phase=k0*distance*np.sin(betta)
    if degrees!=None:
        phase=phase*180/np.pi   #convert to degrees
    return phase

if __name__=="__main__":

    E_elementary=far_field(lumapi.FDTD(filename_fdtd),1)
    # N_a=5           #5 antennas
    # distance=1e-6      
    # E_af=calculate_field(E0=E_elementary,N_a=N_a,distance=distance,betta=-30*np.pi/180)
    # plot_field(E_af)
