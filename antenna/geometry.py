from variables import *
def geometry(sim,margin,group_N):
    sim.switchtolayout()
    sim.addstructuregroup()
    sim.set("name", f"geometry{group_N}")
    sim.set("x",0)
    sim.set("y",0)
    sim.set("z",0)

    # draw clad
    sim.addrect()
    sim.set("name", "clad")
    sim.addtogroup(f"geometry{group_N}")
    sim.set("material", material_Clad)
    sim.set("y", 0+margin)
    sim.set("y span", Y_span + 1e-6)
    sim.set("z min", 0)
    sim.set("z max", thick_Si + thick_Clad)
    sim.set("x min", Xmin)
    sim.set("x max", Xmax)
    sim.set("override mesh order from material database", 1)
    sim.set("mesh order", 2)  # similar to "send to back"
    sim.set("alpha", 0.5)

    # draw buried oxide
    sim.addrect()
    sim.set("name", "BOX")
    sim.addtogroup(f"geometry{group_N}")
    sim.set("material", material_BOX)
    sim.set("x min", Xmin)
    sim.set("x max", Xmax)
    sim.set("y", 0+margin)
    sim.set("y span", Y_span + 1e-6)
    sim.set("z min", -thick_BOX)
    sim.set("z max", 0)
    sim.set("alpha", 0.5)

    # draw silicon wafer
    sim.addrect()
    sim.set("name", "Wafer")
    sim.addtogroup(f"geometry{group_N}")
    sim.set("material", material_Si)
    sim.set("x min", Xmin)
    sim.set("x max", Xmax)
    sim.set("z max", -thick_BOX)
    sim.set("z min", -thick_BOX - 2e-6)
    sim.set("y", 0+margin)
    sim.set("y span", Y_span + 1e-6)
    sim.set("alpha", 0.4)

    # draw waveguide
    sim.addrect()
    sim.set("name", "waveguide")
    sim.addtogroup(f"geometry{group_N}")
    sim.set("material", material_Si)
    sim.set("x min", Xmin)
    sim.set("x max", Xmax)
    sim.set("z min", 0)
    sim.set("z max", thick_Si)
    sim.set("y", 0+margin)
    sim.set("y span", width_Si)
    sim.set("override mesh order from material database", 1)
    sim.set("mesh order", 1)  # similar to "send to back"


    # define grating
    xo = Xmin + 10e-6
    material_gap = "etch"
    xpos = xo
    for i in range(1, N):
        sim.addrect()
        sim.set("name", "grating_gap")
        sim.addtogroup(f"geometry{group_N}")
        sim.set("material", material_gap)

        sim.set("x", xpos + 0.5 * l_g * (1 - dc))
        sim.set("x span", l_g * (1 - dc))

        sim.set("y", 0+margin)
        sim.set("y span", Y_span + 1e-6)

        sim.set("z min", thick_Si + t_r)
        sim.set("z max", thick_Si + t_r + t_g)

        xpos = xpos + l_g


def array_geometry(sim,distance,N_a):
    sim.switchtolayout()
    sim.deleteall()
    for m in range(N_a):
        margin=(distance+width_Si)*m
        g=geometry(sim,margin=margin,group_N=m)



if __name__=="__main__":
    pass