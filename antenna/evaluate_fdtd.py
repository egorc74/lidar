from fdtd_simulation import *

def evaluate_fdtd(sim,m,plot=None):
    # fdtd_setup(sim)
  
    f = 2  
    result = sim.getresult(m, "E")
    Ex= sim.getdata(m,"Ex")
    Ey= sim.getdata(m,"Ey")
    Ez= sim.getdata(m,"Ez")
    Ex1=Ex[:,:,0,f] #[x points , y points, z points, frequency points]
    Ey1=Ey[:,:,0,f]
    Ez1=Ez[:,:,0,f]
    
    E_mag1 = np.sqrt(Ex1**2+Ey1**2+Ez1**2)
    E_mag1 /= np.max(np.abs(E_mag1))
    x = result['x']
    y = result['y']
    if(plot!=None):
        plt.imshow(np.abs(E_mag1).T, extent = [np.min(y)*1e6, np.max(y)*1e6, np.min(x)*1e6, np.max(y)*1e6], aspect = 'auto', origin = 'lower', cmap = 'jet')
        plt.xlabel('x (um)')
        plt.ylabel('y (um)')
        plt.colorbar()
        plt.show()
    
    return E_mag1,x,y


def exp_func(x, b):
    return  np.exp(b * x)

from scipy.optimize import curve_fit

def perturbation_curve_fitting(sim,m,plot=None):
    E_mag,x,y=evaluate_fdtd(sim,m)
    x=x.flatten()
    x_val=x[1:] + np.abs(x[0]) 
    E_values= np.abs(E_mag[1:, 25])
    popt, pcov = curve_fit(exp_func, x_val, E_values)
    b = popt
    y_fit=exp_func(x_val,b)

    print(b/1000)   #db/mm not m
    if(plot!=None):
        plt.plot(x_val*1e6, E_values, label=f'curve {25+1}')  # x in micrometers
        plt.plot(x_val*1e6, y_fit, label=f'curve {25+1}')  # x in micrometers
        plt.xlabel("x (µm)")
        plt.ylabel("Value")
        plt.title("51 curves vs x")
        #If you want the legend, uncomment below (but it may get messy with 51 labels):
        plt.legend()
        plt.show()
            
        x_len=np.linspace(0,1,1000)*1e-3
        y_len=exp_func(x_len,b)
        plt.plot(x_len*1e6, y_len, label=f'curve for 1 mm length')  # x in micrometers
        plt.xlabel("x (µm)")
        plt.ylabel("Value")
        plt.title("1 mm length antenna")
        #If you want the legend, uncomment below (but it may get messy with 51 labels):
        plt.legend()
        plt.show()

def directionality_calculation(sim,plot=None):
    monitors=["top_m","bottom_m","side_m","back_m","forward_m"]
    T_p=[]
    x=None
    for m in monitors:
        result = sim.getresult(m, "T")
        T=result['T']
        T_p.append(np.abs(T[2])) 

    
    directionality=T_p[0]/(T_p[1]+2*T_p[2]+T_p[3]+T_p[0])           #actually true 
    print(directionality)
    return directionality