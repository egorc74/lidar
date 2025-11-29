from variables import *


#######################################
#######################################
####    WIDTH OF INPUT TAPER AT THE EDGE OF A CHIP      W_input 
####    NUMBER OF INPUT TAPERS                          Num_input
####    GAP BETWEEN INPUTS                              Gap_input   
####    TAPER LENGTH FROM THE EDGE TO THE COMBINER      Len_evolv
####    WIDTH OF TAPER AT COMBINER-TAPER SUFACE         W_edge
####    GAP BETWEEN TAPERS                              Gap_edge
####    DISTANCE FROM THE HORIZONTAL EDGES OF COMBINER  D_comb
####    WIDTH OF COMBINER                               W_comb
####    LENGTH OF COMBINER                              Len_comb

def geometry(sim,filename,W_input,Num_input,Gap_input,Len_evolv,W_edge,Gap_edge,D_comb,Len_comb,wg_width):
    log = setup_logger("mode_geometry", "logging/mode_geometry.log")

    log.info(f"Starting mode_geometry() built \n W_input: {W_input},"
             f"\nNumber of inputs:{Num_input},\n Gap between iputs={Gap_input},\n"
              f"\nLength from the edge to combiner(mode evolution) :{Len_evolv}"
              f"\nWidth of taper at combiner-taper surface: {W_edge}"
              f"\nGap between Taper {Gap_edge}"
              f"\nDistance from the combiner edger to the first taper{D_comb}"
              f"\nLength of combiner {Len_comb}")

#Clear all
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

#Draw combiner

    sim.addstructuregroup()
    sim.set("name","Chip")
   

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

    sim.select("Combiner")
    sim.addtogroup("::model::Chip")

#Draw input tapers
## Add polygons with vertices 

    for N in range(Num_input):
        ly_combiner=W_edge
        x_span=Len_evolv
        z_span=thick_Si
        z=0
        x=-Len_evolv/2
        y=Comb_start-N*(Gap_edge+W_edge)
        ly_horizontal=W_input
        V = np.zeros((4, 2))
        surf_y=Surf_start-N*(Gap_input+W_input)


        # assign values row by row
        V[0, :] = [-x_span/2, surf_y-W_input/2]
        V[1, :] = [-x_span/2,surf_y+W_input/2]
        V[2, :] = [  x_span/2,y+W_edge/2]
        V[3, :] = [ x_span/2,y-W_edge/2]

        sim.addpoly()
        sim.set("x",x)
        sim.set("y",0)
        sim.set("z",z)
        sim.set("z span",z_span)
        sim.set("vertices",V)
        sim.set("material",material_Si)
        sim.set("name",f"Taper_{N}")
        sim.set("override mesh order from material database",1)
        sim.set("mesh order",1)
        sim.select(f"Taper_{N}")
        sim.addtogroup("::model::Chip")



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
    sim.select(f"Clad")
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
    
    sim.select(f"BOX")
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
    sim.select(f"Wafer")
    sim.addtogroup("::model::Chip")

    sim.save(filename)
    
     





if __name__=="__main__":
    filename="mode_edge_coupler"
    W_input=0.18e-6
    Num_input=4
    Gap_input=0.680e-6
    Len_evolv=70e-6
    W_edge=0.290e-6
    Gap_edge=0.15e-6
    D_comb=0.2e-6
    Len_comb=20e-6
    wg_width=0.55e-6
    geometry(sim=lumapi.MODE(),
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





    