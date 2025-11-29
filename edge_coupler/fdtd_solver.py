from variables import *
from fdtd_geometry import geometry
def fdtd_solver(sim,filename,kwargs):
    


    W_input=kwargs.get("W_input")
    Num_input=kwargs.get("Num_input")
    Gap_input=kwargs.get("Gap_input")
    Len_evolv=kwargs.get("Len_evolv")
    W_edge=kwargs.get("W_edge")
    Gap_edge=kwargs.get("Gap_edge")
    D_comb=kwargs.get("D_comb")
    Len_comb=kwargs.get("Len_comb")
    wg_width=kwargs.get("wg_width")

    print(W_input)
    mesh_accuracy=kwargs.get("mesh_accuracy")

    log = setup_logger("fdtd_solver", "logging/fdtd_solver.log")

    log.info(f"Starting fdtd_solver() built \n W_input: {W_input},"
             f"\nNumber of inputs:{Num_input},\n Gap between iputs={Gap_input},\n"
              f"\nLength from the edge to combiner(mode evolution) :{Len_evolv}"
              f"\nWidth of taper at combiner-taper surface: {W_edge}"
              f"\nGap between Taper {Gap_edge}"
              f"\nDistance from the combiner edger to the first taper{D_comb}"
              f"\nLength of combiner {Len_comb}")

    geometry(sim=sim,
            filename=filename,
            W_input=W_input,
            Num_input=Num_input,
            Gap_input=Gap_input,
            Len_evolv=Len_evolv,
            W_edge=W_edge,
            Gap_edge=Gap_edge,
            D_comb=D_comb,
            Len_comb=Len_comb,
            wg_width=wg_width)
#add fdtd region


    W_comb=Num_input*W_edge+(Num_input-1)*Gap_edge+2*D_comb
    W_surface=Num_input*W_input+(Num_input-1)*Gap_input    #whole surface of coupling 

    X_min=-Len_evolv-3e-6
    X_max=Len_comb+3e-6


    sim.addfdtd()
    sim.set("dimension", 2)
    sim.set("y", 0)
    sim.set("y span", W_surface+2e-6)
    
    sim.set("x min", X_min)
    sim.set("x max", X_max)
    sim.set("z", thick_Si / 2)
    sim.set("z span", 3e-6)

    sim.set("z min", -thick_BOX-0.1e-6)
    sim.set("z max", thick_Si+thick_Clad+0.2e-6)

    sim.set("mesh accuracy", mesh_accuracy)
    sim.set("y min bc", "PML")



    
    

#add set global source
    sim.setglobalsource("wavelength start",wavelength)
    sim.setglobalsource("wavelength stop",wavelength)

    sim.setglobalmonitor("use source limits",0)
    sim.setglobalmonitor("frequency points",1)
    sim.setglobalmonitor("wavelength center",wavelength)


# #add Gaussian 

#     sim.addgaussian()
#     sim.set("injection axis","x")
#     sim.set("direction","forward")
#     sim.set("x",X_min+1e-6)
#     sim.set("y",0)
#     sim.set("y span",10e-6)
#     sim.set("z",0)
#     sim.set("z span",10e-6)

#     sim.set("use scalar approximation",1)
#     sim.set("waist radius w0",4e-6)
#     sim.set("distance from waist",-2e-6)


##Input port

    sim.addport()
    sim.set("name","input_port")
    sim.set("injection axis","x-axis")
    sim.set("direction","forward")
            
    sim.set("y span",10e-6)
    sim.set("y",0) 
    sim.set("x",X_min+1e-6) 
    sim.set("z",0) 
    sim.set("z span",10e-6)


##Through port

    sim.addport()
    sim.set("name","through_port")
    sim.set("injection axis","x-axis")
    sim.set("direction","backward")
            
    sim.set("y span",wg_width+2e-6)
    sim.set("y",0) 
    sim.set("x",X_max-1e-6) 
    sim.set("z",0) 
    sim.set("z span",thick_Si+0.5e-6)


    sim.adddftmonitor()
    sim.set("x span",200e-6)
    sim.set("y span",20e-6)
    sim.set("x",0)
    sim.set("y",0)
    sim.set("z",0)

#add mesh for tapers
    for n_tap in range(Num_input):
        sim.addmesh()
        sim.set('dy',0.02e-6)
        sim.set('dz',0.02e-6)
        sim.set('override x mesh',0)
        sim.set('based on a structure',1)  
        sim.set('structure',f'Taper_{n_tap}')  
        sim.set('buffer',0.1e-6)  
        sim.set('name',f'taper_mesh_{n_tap}') 



    sim.save(f"{filename}.fsp")
    
    #run fdtd

    # sim.run()


    input("Press Enter to continue...")

    # #get results from both monitors
    m2_name="through_port"

    try:
        T_through = sim.getresult(m2_name,"T")
        log.info(f"Obtained T_through {T_through}")

    except Exception as e:
        T_through=0
        log.error(f"Error occured: {e} Obtained T_through {T_through}")


    sim.save(f"{filename}.fsp")

    return T_through

if __name__=="__main__":
    filename='fdtd_edge_coupler'
    kwargs={
    'W_input': 0.102e-6,
    'Num_input': 5,
    'Gap_input':0.970e-6,
    'Len_evolv':50e-6,
    'W_edge':0.290e-6,
    'Gap_edge':0.15e-6,
    'D_comb':0.1e-6,
    'Len_comb':15e-6,
    'wg_width':0.55e-6,
    'mesh_accuracy':2
    }
    fdtd_solver(sim=lumapi.FDTD(),filename=filename,kwargs=kwargs)
    


   

