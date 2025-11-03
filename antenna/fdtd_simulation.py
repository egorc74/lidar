from geometry import *
from phased_array_field_profile import phase_calculation
def fdtd_setup(sim,betta,wavelength,N_a):
    distance=1e-6
    array_geometry(sim,distance=distance,N_a=N_a)
    sim.addfdtd()
    sim.set("dimension", 2)
    sim.set("y", 0)
    sim.set("y min", -4e-6 / 2)
    sim.set("y max", 4e-6 / 2 + (distance+width_Si)*(N_a-1))
    
    sim.set("x min", -l/2 - 5e-6)
    sim.set("x max", l/2 + 2e-6)
    sim.set("z", thick_Si / 2)
    sim.set("z span", 3e-6)

    sim.set("z min", -thick_BOX-0.1e-6)
    sim.set("z max", thick_Si+thick_Clad+0.2e-6)

    sim.set("mesh accuracy", 2)
    sim.set("y min bc", "PML")



    mesh_override_dx=l_g/20 #must be an integer of grating
    sim.addmesh()
    sim.set("y min", -4e-6/2)
    sim.set("y max", (4e-6/2+(distance+width_Si)*(N_a-1)))
    sim.set("x min", -l/2 - 200*l_g/2)
    sim.set("x max", l/2 + 200*l_g/2)
    sim.set("z min", 0)
    sim.set("z max", thick_Clad)
    sim.set('dx',mesh_override_dx)
    sim.set('override y mesh',0)
    sim.set('override z mesh',0)

    set_global(wavelength=wavelength,sim=sim)
    add_modes(betta=betta,wavelength=wavelength,distance=distance,sim=sim,N_a=N_a-1)
    
    
    # # Add profile monitor near source
    # sim.adddftmonitor()    
    # sim.set("monitor type", 7)
    # sim.set("z", thick_Si / 2)
    # sim.set("x min", -l/2 - 2e-6)
    # sim.set("x max", l/2 + 2e-6)
    # sim.set("y", 0)
    # sim.set("y span", 2e-6)
    # sim.set("override global monitor settings",1)
    # sim.set("name","wg_monitor")
    

    # Add far-field profile monitor
    sim.adddftmonitor()
    sim.set("monitor type", 7) #2D Z normal
    sim.set("z", thick_Si + thick_Clad + 0.05e-6)
    sim.set("x min", -l/2 - 2e-6)
    sim.set("x max", l/2 + 2e-6)

    sim.set("y min", -5e-6 / 2)
    sim.set("y max", 5e-6 / 2 + (distance+width_Si)*(N_a-1))
    
    sim.set("name","top_m")


#    # Add Bottom -z monitor
#     sim.adddftmonitor()
#     sim.set("monitor type", 7) #2D Z normal
#     sim.set("z", -thick_BOX/2)
#     sim.set("x min", -l/2 - 2e-6)
#     sim.set("x max", l/2 + 2e-6)
#     sim.set("y", 0)
#     sim.set("y span", 5e-6)
#     sim.set("name","bottom_m")

   
    
#    # Add side +y monitor
#     sim.adddftmonitor()
#     sim.set("monitor type", "2D Y-normal") #2D Z normal
#     sim.set("z",thick_Si / 2)
#     sim.set("z span",3e-6)
    
#     sim.set("x min", -l/2 - 2e-6)
#     sim.set("x max", l/2 + 2e-6)
#     sim.set("y", 1e-6)
#     sim.set("name","side_m")

   
    #  # Add back reflection x monitor
    # sim.adddftmonitor()
    # sim.set("monitor type", "2D X-normal") #2D Z normal
    # sim.set("z",thick_Si / 2)
    # sim.set("z span",3e-6)
    
    # sim.set("x", -l/2 - 2e-6)
    # sim.set("z", thick_Si / 2)
    # sim.set("z span", 2e-6)
    # sim.set("y", 0)
    # sim.set("y span", Y_span)
    # sim.set("name","back_m")

      # Add x normal at the end monitor
    sim.adddftmonitor()
    sim.set("monitor type", "2D X-normal") #2D Z normal
    sim.set("z",thick_Si / 2)
    sim.set("z span",3e-6)
    
    sim.set("x", l/2-1e-6)
    sim.set("z", thick_Si / 2)
    sim.set("z span", 2e-6)
    sim.set("y", 0)
    sim.set("y span",  width_Si+0.5e-6)
    sim.set("name","forward_m")


    # Add x normal at the end for 2nd wg
    sim.adddftmonitor()
    sim.set("monitor type", "2D X-normal") #2D Z normal
    sim.set("z",thick_Si / 2)
    sim.set("z span",3e-6)
    
    sim.set("x", l/2-1e-6)
    sim.set("z", thick_Si / 2)
    sim.set("z span", 2e-6)
    sim.set("y", distance+width_Si)
    sim.set("y span", width_Si+0.5e-6)
    sim.set("name","second_forward_m")

    sim.save(filename_fdtd)
    # sim.run()
    sim.save(filename_fdtd)



def add_modes(sim,N_a,distance,betta,wavelength):
    phase=phase_calculation(wavelength=wavelength,distance=distance,betta=betta,degrees=1)
    for m in range(N_a):
        margin=(distance+width_Si) * m
        sim.addmode()
        sim.set("center wavelength", wavelength)
        sim.set("wavelength span", 0.e-6)
        sim.set("x", -l/2 - 1e-6)
        sim.set("z", thick_Si / 2)
        sim.set("z span", 2e-6)
        sim.set("y", margin)
        sim.set("y span", (distance+width_Si))
        sim.set("mode selection", 4)
        sim.set("override global source settings",0)
        sim.set("phase",phase*m)
        # Pick correct mode manually (or script the logic if needed)
        correct_mode = 1
        sim.set("selected mode number", correct_mode)

def set_global(sim,wavelength):
    sim.setglobalsource("wavelength start",wavelength-0.05e-6)
    sim.setglobalsource("wavelength stop",wavelength+0.05e-6)

    sim.setglobalmonitor("use source limits",0)
    sim.setglobalmonitor("frequency points",100)
    sim.setglobalmonitor("wavelength center",wavelength)
    sim.setglobalmonitor("wavelength span",0.1e-6)
        








if __name__=="__main__":
    fdtd=lumapi.FDTD(filename_fdtd)
    betta=30*np.pi/180
    wavelength=1.55e-6
    fdtd_setup(fdtd,wavelength=wavelength,betta=betta,N_a=2)
    