from variables import *
from pso_utils import get_mode_overlapp_fiber_to_chip,get_mode_overlapp_tapers_to_combiner,input_pso_geometry,combiner_edge_pso_geometry

import pyswarms as ps
from pyswarms.utils.functions import single_obj as fx
from pyswarms.utils.plotters import (plot_cost_history, plot_contour, plot_surface)


##################################################################################################
## FIRST WE NEED A FITTING FUNCTION, WHICH WILL BE A MODE OVERLAPP OF FIBER MODE AND COUPLER MODE S
## Fiting function --- get_mode_overlapp() with input_pso_geometry() ---returns mode overlap
## inputs --- W_input, Gap_input, Num_of_modes --- three dimensions 
##

def fittingfunction_fiber_to_chip(x):

    #we need to itterate through each of the particle
    filename="mode_edge_coupler"
    itteration_overlaps=[]
    for p in range(x.shape[0]):     
        W_input=x[p,0]
        Num_input=x[p,1].round().astype(int)
        Gap_input=x[p,2]
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
        overlap=-get_mode_overlapp_fiber_to_chip(sim)
        print(overlap)
        itteration_overlaps.append(overlap)
    return itteration_overlaps

def fittingfunction_taper_to_combiner(x):
    
    ### Currently best found option is W_in=0.102e-6 Num_in=5 Gap=0.970e-6 

    #we need to itterate through each of the particle
    filename="mode_edge_coupler"
    itteration_overlaps=[]
    for p in range(x.shape[0]):     
        W_input=0.102e-6
        Num_input=5
        Gap_input=0.97e-6
        Len_evolv=70e-6
        W_edge=x[p,0]
        Gap_edge=x[p,1]
        D_comb=x[p,2]
        Len_comb=20e-6
        wg_width=0.55e-6
        sim=lumapi.MODE(filename)
        combiner_edge_pso_geometry(sim=sim,
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
        overlap=-get_mode_overlapp_tapers_to_combiner(sim)
        print(overlap)
        itteration_overlaps.append(overlap)
    return itteration_overlaps


def pso_fiber_to_chip(itterations,num_of_particles):
    #first dimension W_input
    #second dimension Num_input
    #third dimension Gap_input

    # Create bounds

    max_bound_1 = 0.300e-6
    max_bound_2 = 6
    max_bound_3 = 1e-6
    
    min_bound_1 = 0.1e-6
    min_bound_2 = 1
    min_bound_3 =0.35e-6

    max_bound=[max_bound_1,max_bound_2,max_bound_3]
    min_bound=[min_bound_1,min_bound_2,min_bound_3]

    bounds = (min_bound, max_bound)
    options = {'c1':0.5, 'c2':0.3, 'w':0.9}
    optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=3, options=options,bounds=bounds)
    cost, pos = optimizer.optimize(fittingfunction_fiber_to_chip,itterations)
    plot_cost_history(cost_history=optimizer.cost_history)
    plt.show()



def pso_taper_to_combiner(itterations,num_of_particles):
    #first dimension W_edge
    #second dimension Gap_edge
    #third dimension D_comb

    # Create bounds

    max_bound_1 = 0.6e-6
    max_bound_2 = 1e-6
    max_bound_3 = 0.5e-6
    
    min_bound_1 = 0.15e-6
    min_bound_2 = 0.15e-6
    min_bound_3 =0e-6

    max_bound=[max_bound_1,max_bound_2,max_bound_3]
    min_bound=[min_bound_1,min_bound_2,min_bound_3]

    bounds = (min_bound, max_bound)
    options = {'c1':0.5, 'c2':0.3, 'w':0.9}
    optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=3, options=options,bounds=bounds)
    cost, pos = optimizer.optimize(fittingfunction_taper_to_combiner,itterations)
    plot_cost_history(cost_history=optimizer.cost_history)
    plt.show()


if __name__=="__main__":

    ### Currently best found option is W_in=0.102e-6 Num_in=5 Gap=0.970e-6 
    #best cost: -1.0731339213517208, best pos: [3.11698237e-07 1.56329249e-07 9.43112336e-08]
    itterations=10
    num_of_particles=3
    # pso_fiber_to_chip(itterations=itterations,num_of_particles=num_of_particles)
    pso_taper_to_combiner(itterations=itterations,num_of_particles=num_of_particles)
    