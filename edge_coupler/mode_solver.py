from variables import *
from mode_geometry import geometry
def mode_solver(sim,filename,W_input,Num_input,Gap_input,
                Len_evolv,W_edge,Gap_edge,D_comb,Len_comb,wg_width):
    
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




    modes=20

#Calculate widths
    W_comb=Num_input*W_edge+(Num_input-1)*Gap_edge+2*D_comb
    W_surface=Num_input*W_input+(Num_input-1)*Gap_input    #whole surface of coupling 

    Y_span=W_surface+3e-6
    meshsize=0.01e-6
    sim.addfde()
    sim.set("solver type","2D X normal")
    sim.set("x",-Len_evolv)
    sim.set("y",0)
    sim.set("y span",10e-6)
    sim.set("z max",5e-6)
    sim.set("z min",-5e-6)
    sim.set("wavelength",wavelength)
    sim.set("solver type","2D X normal")
    sim.set("define y mesh by","maximum mesh step") 
    sim.set("dy",meshsize)
    sim.set("define z mesh by","maximum mesh step") 
    sim.set("dz",meshsize)
    sim.set("number of trial modes",modes)
    input("press enter")
    sim.save(filename)




if __name__=="__main__":
    filename="mode_effective_index"
    taper_width=2.5e-6
    width_ridge=8e-6

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

    mode_solver(sim=lumapi.MODE(filename),
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




