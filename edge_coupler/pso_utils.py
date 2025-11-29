from variables import *

def input_pso_geometry(sim,filename,W_input,Num_input,Gap_input,Len_evolv,W_edge,Gap_edge,D_comb,Len_comb,wg_width):
    sim.switchtolayout()
    sim.deleteall()

#Calculate widths
    W_comb=Num_input*W_edge+(Num_input-1)*Gap_edge+2*D_comb
    W_surface=Num_input*W_input+(Num_input-1)*Gap_input    #whole surface of coupling 

    Comb_start=W_comb/2 - D_comb - W_edge/2    #taper array start at combiner surface
    Surf_start=W_surface/2 - W_input/2          #taper array start at coupling surface

#Simulation boarders
    Y_span=W_surface+5e-6
    X_span=Len_comb+Len_evolv
    X_min=-Len_evolv
    X_max=Len_comb+10e-6


#add SMF-28 fiber (planar polished)
    sim.addstructuregroup()
    sim.set("name","SMF_28")
    
    
    Len_fiber=30e-6
    Core_radius=8.2e-6/2
    Cladd_radius=20e-6   
    #fiber core
    sim.addcircle()
    sim.set("x",X_min-Len_fiber/2)
    sim.set("y",0)
    sim.set("z",0)
    sim.set("z span",Len_fiber)
    sim.set("radius",Core_radius)
    sim.set("index",SMF_28_core_index)
    sim.set("first axis","y")
    sim.set("rotation 1",-90)
    sim.set("name","SMF_28_core")
    sim.set("override mesh order from material database",1)
    sim.set("mesh order",1)
    sim.select("SMF_28_core")
    sim.addtogroup("::model::SMF_28")

    #fiber cladding
    sim.addcircle()
    sim.set("x",X_min-Len_fiber/2)
    sim.set("y",0)
    sim.set("z",0)
    sim.set("z span",Len_fiber)
    sim.set("radius",Cladd_radius)
    sim.set("index",SMF_28_cladd_index)
    sim.set("first axis","y")
    sim.set("rotation 1",-90)
    sim.set("name","SMF_28_cladd")
    sim.set("override mesh order from material database",1)
    sim.set("mesh order",2)
    sim.set("alpha",0.3)

    sim.select("SMF_28_cladd")
    sim.addtogroup("::model::SMF_28")



#Create structure group for PSO sweeps


    sim.addstructuregroup()
    sim.set("name","Chip")
    

    #add width input, number of inputs and input gap as input parameters
    sim.addstructuregroup()
    sim.set("name","input tapers")
    sim.adduserprop("W_input",2,W_input)
    sim.adduserprop("Num_input",0,Num_input)
    sim.adduserprop("Gap_input",2,Gap_input)

    sim.set("construction group",1)

#add rectangle to structure by setting script

    sim.set('script',f"""
        W_surface=Num_input*W_input+(Num_input-1)*Gap_input;    
        Surf_start=W_surface/2 - W_input/2;
        for (nn=0:(Num_input-1)){{
        surf_y={Surf_start}-nn*(Gap_input+W_input);
        addrect;
        set("x",{-Len_evolv/2});
        set("y",surf_y);
        set("z",0);
        set("z span",{thick_Si});
        set("x span",{Len_evolv});
        set("y span",W_input);
        set("material","{material_Si}");
        set("name","Taper_"+num2str(nn));
        set("override mesh order from material database",1);
        set("mesh order",1);}}
    """
    )
    sim.select("input tapers")
    sim.addtogroup("::model::Chip")

#draw cladd
    sim.addrect()
    sim.set("name","Clad") 
    sim.set("material",material_Clad)
    sim.set("y",0)         
    sim.set("y span",Y_span)
    sim.set("z min",-thick_Si/2)     
    sim.set("z max", thick_Clad)
    sim.set("x min",X_min)
    sim.set("x max",X_max)
    sim.set("alpha",0.05)
    sim.set("override mesh order from material database",1)
    sim.set("mesh order",4)
    sim.select("Clad")
    sim.addtogroup("::model::Chip")


#draw box and waffer
    sim.addrect() 
    sim.set("name","BOX") 
    sim.set("material",material_BOX)
    sim.set("y",0)         
    sim.set("y span",Y_span)
    sim.set("z min",-thick_BOX-thick_Si/2)     
    sim.set("z max", 0-thick_Si/2)
    sim.set("x min",X_min)
    sim.set("x max",X_max)
    sim.set("alpha",0.05)
    sim.select("BOX")
    sim.addtogroup("::model::Chip")

#draw waffer
    sim.addrect() 
    sim.set("name","Wafer") 
    sim.set("material",material_Si)
    sim.set("y",0)         
    sim.set("y span",Y_span+5e-6)
    sim.set("z min",-thick_BOX-thick_Substrate)     
    sim.set("z max", -thick_BOX)
    sim.set("x min",X_min)  
    sim.set("x max",X_max)
    sim.set("alpha",0.1)
    sim.select("Wafer")
    sim.addtogroup("::model::Chip")
    sim.save(filename)
     

#Add fde
    modes=20
    meshsize=0.1e-6
    sim.addfde()
    sim.set("solver type","2D X normal")
    sim.set("x",-Len_evolv)
    sim.set("y",0)
    sim.set("y span",Core_radius*2+4e-6)
    sim.set("z",0)
    sim.set("z span",Core_radius*2+4e-6)
    sim.set("wavelength",wavelength)
    sim.set("solver type","2D X normal")
    sim.set("define y mesh by","maximum mesh step") 
    sim.set("dy",meshsize)
    sim.set("define z mesh by","maximum mesh step") 
    sim.set("dz",meshsize)
    sim.set("number of trial modes",modes)
#add mesh for each taper
    for n_tap in range(Num_input):
        sim.addmesh()
        sim.set('dy',0.01e-6)
        sim.set('dz',0.01e-6)
        sim.set('based on a structure',1)  
        sim.set('structure',f'Taper_{n_tap}')  
        sim.set('buffer',0.1e-6)  
        sim.set('name',f'taper_mesh_{n_tap}') 

    sim.save(filename)


##################################
####################################
###  For combiner edge pso

def combiner_edge_pso_geometry(sim,filename,W_input,Num_input,
                               Gap_input,Len_evolv,W_edge,
                               Gap_edge,D_comb,Len_comb,wg_width):
    

    sim.switchtolayout()
    sim.deleteall()

#Calculate widths
    W_comb=Num_input*W_edge+(Num_input-1)*Gap_edge+2*D_comb
    W_surface=Num_input*W_input+(Num_input-1)*Gap_input    #whole surface of coupling 

    Comb_start=W_comb/2 - D_comb - W_edge/2    #taper array start at combiner surface
    Surf_start=W_surface/2 - W_input/2          #taper array start at coupling surface

#Simulation boarders
    Y_span=W_comb+5e-6
    X_span=Len_comb+Len_evolv
    X_min=-Len_evolv
    X_max=Len_comb+10e-6



#Create structure group for PSO sweeps


    sim.addstructuregroup()
    sim.set("name","Input tapers")
    

#add rectangles
    
    for N in range(Num_input):
        ly_combiner=W_edge
        x_span=Len_evolv
        z_span=thick_Si
        z=0
        x=-Len_evolv/2
        y=Comb_start-N*(Gap_edge+W_edge)
        sim.addrect()
        sim.set("x",x)
        sim.set("y",y)
        sim.set("z",z)
        sim.set("x span",x_span)
        sim.set("y span",ly_combiner)
        sim.set("z span",z_span)
        sim.set("material",material_Si)
        sim.set("name",f"Taper_{N}")
        sim.set("override mesh order from material database",1)
        sim.set("mesh order",1)
        sim.select(f"Taper_{N}")
        sim.addtogroup("::model::Input tapers")


#Draw combiner

    ly_top=wg_width #width of wg        
    ly_base=W_comb
    x_span=Len_comb
    z_span=thick_Si
    z=0
    x=Len_comb/2
    y=0

    V = np.zeros((4, 2))

    # assign values row by row
    V[0, :] = [-ly_base/2, -x_span/2]
    V[1, :] = [-ly_top/2,  x_span/2]
    V[2, :] = [ ly_top/2,  x_span/2]
    V[3, :] = [ ly_base/2, -x_span/2]

    sim.addpoly()
    sim.set("x",x)
    sim.set("y",0)
    sim.set("z",z)
    sim.set("z span",z_span)
    sim.set("vertices",V)
    sim.set("material",material_Si)
    sim.set("name","Combiner")
    sim.set("first axis","z")
    sim.set("rotation 1",-90)
    sim.set("override mesh order from material database",1)
    sim.set("mesh order",1)

#draw cladd
    sim.addrect()
    sim.set("name","Clad") 
    sim.set("material",material_Clad)
    sim.set("y",0)         
    sim.set("y span",Y_span)
    sim.set("z min",-thick_Si/2)     
    sim.set("z max", thick_Clad)
    sim.set("x min",X_min)
    sim.set("x max",X_max)
    sim.set("alpha",0.05)
    sim.set("override mesh order from material database",1)
    sim.set("mesh order",4)


#draw box and waffer
    sim.addrect() 
    sim.set("name","BOX") 
    sim.set("material",material_BOX)
    sim.set("y",0)         
    sim.set("y span",Y_span)
    sim.set("z min",-thick_BOX-thick_Si/2)     
    sim.set("z max", 0-thick_Si/2)
    sim.set("x min",X_min)
    sim.set("x max",X_max)
    sim.set("alpha",0.05)

#draw waffer
    sim.addrect() 
    sim.set("name","Wafer") 
    sim.set("material",material_Si)
    sim.set("y",0)         
    sim.set("y span",Y_span+5e-6)
    sim.set("z min",-thick_BOX-thick_Substrate)     
    sim.set("z max", -thick_BOX)
    sim.set("x min",X_min)  
    sim.set("x max",X_max)
    sim.set("alpha",0.1)
    sim.save(filename)
     

#Add fde
    modes=20
    meshsize=0.05e-6
    sim.addfde()
    sim.set("solver type","2D X normal")
    sim.set("x",0)
    sim.set("y",0)
    sim.set("y span",W_comb+4e-6)
    sim.set("z",0)
    sim.set("z span",thick_Clad*2)
    sim.set("wavelength",wavelength)
    sim.set("solver type","2D X normal")
    sim.set("define y mesh by","maximum mesh step") 
    sim.set("dy",meshsize)
    sim.set("define z mesh by","maximum mesh step") 
    sim.set("dz",meshsize)
    sim.set("number of trial modes",modes)
#add mesh for each taper
    for n_tap in range(Num_input):
        sim.addmesh()
        sim.set('dy',0.01e-6)
        sim.set('dz',0.01e-6)
        sim.set('based on a structure',1)  
        sim.set('structure',f'Taper_{n_tap}')  
        sim.set('buffer',0.1e-6)  
        sim.set('name',f'taper_mesh_{n_tap}') 

#add mesh for combiner
    sim.addmesh()
    sim.set('dy',0.01e-6)
    sim.set('dz',0.01e-6)
    sim.set('based on a structure',1)  
    sim.set('structure','Combiner')  
    sim.set('buffer',0.1e-6)  
    sim.set('name','Combiner_mesh') 
    sim.save(filename)
    





def get_mode_overlapp_fiber_to_chip(sim,**kwargs):
    sim.switchtolayout()

#first calculate mode of fiber
    #disable chip
    sim.select("Chip")
    sim.set("enabled",0)
    #enable fiber
    sim.select("SMF_28")
    sim.set("enabled",1)
    sim.setnamed("FDE","z span",12e-6)

#calculate mode for fiber 
    sim.run()
    sim.cleardcard()
    n=sim.findmodes()
    
    #select first TE mode and add it to d-card

    for mode in range(20):
        mode_polarization=sim.getdata(f'FDE::data::mode{mode+1}','TE polarization fraction')
        # select first TE mode
        if mode_polarization>0.95:
            sim.copydcard(f"mode{mode+1}","fiber_mode")
            break
 
#second calculate mode of chip
    sim.switchtolayout()
    #enable chip
    sim.select("Chip")
    sim.set("enabled",1)
    #disable fiber
    sim.select("SMF_28")
    sim.set("enabled",0)
    #narrow fde sim region, for avoiding quasi modes in the substrate
    sim.setnamed("FDE","z span",3e-6)
    # sim.setnamed("FDE","dy",0.01e-6)
    # sim.setnamed("FDE","dz",0.01e-6)

#calculate mode for chip 
    n=sim.findmodes()
    #select first TE mode and add it to d-card

    for mode in range(20):
        mode_polarization=sim.getdata(f'FDE::data::mode{mode+1}','TE polarization fraction')
        print(mode_polarization)
        # select first TE mode
        if mode_polarization>0.95:
            sim.copydcard(f"mode{mode+1}","chip_TE_mode")
            break
    overlap=sim.overlap("chip_TE_mode","fiber_mode")
    return overlap[0][0]



def get_mode_overlapp_tapers_to_combiner(sim,**kwargs):
    sim.switchtolayout()

#first calculate mode of fiber
    #disable chip
    sim.select("Input tapers")
    sim.set("enabled",0)
    #enable fiber
    sim.select("Combiner")
    sim.set("enabled",1)

#calculate mode for fiber 
    sim.run()
    sim.cleardcard()
    n=sim.findmodes()
    
    #select first TE mode and add it to d-card

    for mode in range(20):
        mode_polarization=sim.getdata(f'FDE::data::mode{mode+1}','TE polarization fraction')
        # select first TE mode
        if mode_polarization>0.95:
            sim.copydcard(f"mode{mode+1}","combiner_mode")
            break
 
#second calculate mode of chip
    sim.switchtolayout()
    #enable chip
    sim.select("Input tapers")
    sim.set("enabled",1)
    #disable fiber
    sim.select("Combiner")
    sim.set("enabled",0)

#calculate mode for chip 
    n=sim.findmodes()
    #select first TE mode and add it to d-card

    for mode in range(20):
        mode_polarization=sim.getdata(f'FDE::data::mode{mode+1}','TE polarization fraction')
        # select first TE mode
        if mode_polarization>0.90:
            sim.copydcard(f"mode{mode+1}","input_tapers_mode")
            break
    overlap=sim.overlap("input_tapers_mode","combiner_mode")
    return overlap[0][0]

if __name__=="__main__":
    filename="mode_edge_coupler"
    W_input=0.102e-6
    Num_input=5
    Gap_input=0.970e-6
    Len_evolv=70e-6
    W_edge=0.290e-6
    Gap_edge=0.15e-6
    D_comb=0.2e-6
    Len_comb=20e-6
    wg_width=0.55e-6
    sim=lumapi.MODE(filename)
    input_pso_geometry(sim=sim,
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
    # combiner_edge_pso_geometry(sim=sim,
    #         filename=filename,
    #         W_input=W_input,
    #         Num_input=Num_input,
    #         Gap_input=Gap_input,
    #         Len_evolv=Len_evolv,
    #         W_edge=W_edge,
    #         Gap_edge=Gap_edge,
    #         D_comb=D_comb,
    #         Len_comb=Len_comb,
    #         wg_width=wg_width)
    input("press enter")
    # print(get_mode_overlapp_tapers_to_combiner(sim))

