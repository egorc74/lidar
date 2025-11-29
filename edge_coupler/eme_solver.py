from mode_geometry import geometry
from variables import *

def eme_solver(sim,filename,kwargs):
    
    W_input=kwargs.get("W_input")
    Num_input=kwargs.get("Num_input")
    Gap_input=kwargs.get("Gap_input")
    Len_evolv=kwargs.get("Len_evolv")
    W_edge=kwargs.get("W_edge")
    Gap_edge=kwargs.get("Gap_edge")
    D_comb=kwargs.get("D_comb")
    Len_comb=kwargs.get("Len_comb")
    wg_width=kwargs.get("wg_width")


    sim.switchtolayout()
    sim.deleteall()
#Build geometry    
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
    




    sim.addeme()
    sim.set("solver type","3D: X Prop")
    center_z_offset=0
    sim.set("wavelength",wavelength)
    sim.set("index",1)
    sim.set("z min",-thick_BOX)
    sim.set("z max", thick_Clad)
        

    sim.set("y",0)         
    sim.set("y span",10e-6+1e-6)
    sim.set("x min",-Len_evolv-1e-6) 
    sim.set("number of cell groups",3)
    sim.set("display cells",1)
    sim.set("number of modes for all cell groups",20)
    sim.set("number of periodic groups",1)
    sim.set("energy conservation","make passive")
    sim.set("subcell method",np.array([0,1,1]))
    sim.set("cells",np.array([1,15,15]))
    sim.set("group spans",np.array([1e-6,Len_evolv,Len_comb]))
    mesh_cells_y=int((11e-6)/wavelength*10)
    sim.set("mesh cells y",mesh_cells_y)
    sim.set("mesh cells z",20)

    sim.set("y min bc","metal")
    sim.set("z min bc","metal")
    sim.set("y max bc","metal")
    sim.set("z max bc","metal")

    sim.set("allow custom eigensolver settings",1)  
    sim.set("modes",np.array([20,50,20]))
    sim.set("mesh cells z",20)

    #input mesh 1

    #add mesh for each taper
    for n_tap in range(Num_input):
        sim.addmesh()
        sim.set('dy',0.01e-6)
        sim.set('dz',0.02e-6)
        sim.set('based on a structure',1)  
        sim.set('structure',f'Taper_{n_tap}')  
        sim.set('buffer',0.1e-6)  
        sim.set('name',f'taper_mesh_{n_tap}') 




    #ports
    #### input 1 #####
    sim.setnamed("EME::Ports::port_1","y",(0))
    sim.setnamed("EME::Ports::port_1","y span",10e-6)
    sim.setnamed("EME::Ports::port_1","z",0)
    sim.setnamed("EME::Ports::port_1","z span",10e-6)
    sim.setnamed("EME::Ports::port_1","mode selection","fundamental TE mode")
    sim.setnamed("EME::Ports::port_1","use full simulation span",0)
  

    sim.setnamed("EME::Ports::port_2","port location","right")
    sim.setnamed("EME::Ports::port_2","y",0)
    sim.setnamed("EME::Ports::port_2","y span",wg_width+1e-6)
    sim.setnamed("EME::Ports::port_2","z min",-thick_BOX)
    sim.setnamed("EME::Ports::port_2","z max",thick_Clad)
    sim.setnamed("EME::Ports::port_2","mode selection","fundamental TE mode")
    sim.setnamed("EME::Ports::port_2","use full simulation span",0)

    #monitors
    sim.addemeprofile()
    sim.set("name","profile")
    sim.set("monitor type","2D Z-normal")
    sim.set("z",0)

    sim.set("y",0)         
    sim.set("y span",11e-6)
    sim.set("x min",-Len_evolv)  
    sim.set("x max",Len_comb)

    sim.save(filename)
    input("enter enter")
    sim.run()


if __name__=="__main__":
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

    filename="eme_edge_coupler"
    eme_solver(sim=lumapi.MODE(),filename=filename,kwargs=kwargs)

