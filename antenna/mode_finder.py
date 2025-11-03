from geometry import *
import pandas as pd
import mplcursors
import os
def mode(sim):
    sim.switchtolayout()
    sim.deleteall()
    print("Starting laying out geometry")
    array_geometry(sim,distance=1e-6,N_a=2)
    sim.addfde()
    sim.set("solver type", 1)
    sim.set("z", 0)
    sim.set("z span", 4e-6)
    sim.set("x", -0.1e-6)
    sim.set("y", 0)
    sim.set("y span", 3e-6)
    sim.set("define y mesh by", 1)
    sim.set("define z mesh by", 1)
    sim.set("dy", 0.02e-6)
    sim.set("dz", 0.02e-6)
    sim.save(filename_mode)

def get_n1_n2_for_given_wavelengths(sim,wavelengths):
    sim.switchtolayout()
    sim.deleteall()
    print("Starting laying out geometry")
    geometry(sim,margin=0,group_N=1)
    sim.addfde()
    sim.set("solver type", 1)
    sim.set("z", 0)
    sim.set("z span", 4e-6)
    sim.set("x", -0.1e-6)
    sim.set("y", 0)
    sim.set("y span", 3e-6)
    sim.set("define y mesh by", 1)
    sim.set("define z mesh by", 1)
    sim.set("dy", 0.02e-6)
    sim.set("dz", 0.02e-6)
    n1_eff=[]
    n2_eff=[]
    for wl in wavelengths:
        #for non etched region
        sim.switchtolayout()
        sim.setnamed("FDE","x",-0.1e-6)
        sim.run()
        sim.mesh()
        sim.setanalysis('wavelength',wl)
        sim.findmodes()
        n1 = np.abs(sim.getresult("mode1", "neff"))
        n1_eff.append(n1)

        #For etched region
        sim.switchtolayout()
        sim.setnamed("FDE","x",0.1e-6)
        sim.run()
        sim.mesh()
        sim.findmodes()
        n2 =np.abs(sim.getresult("mode1", "neff"))
        n2_eff.append(n2)


    df = pd.DataFrame({
        'wavelength': wavelengths,
        'n1': n1_eff,
        'n2': n2_eff
    })
    df.to_csv('refractive_indices.csv', index=False)

def mode_analysis(sim):
    mode(sim)
    E = sim.getresult("mode1", "E")
    return E

def parameter_setup(name, parameter, start, stop):
    # define the parameter thickness
    para = {
        "Name": name,
        "Parameter": f"::model::geometry::waveguide::{parameter}", 
        "Type": "Length",
        "Start": start,
        "Stop": stop,
        "Units": "microns"
    }
    return para

def result_setup(name, number):
    # define results
    result = {
        "Name": name,
        "Result": f"::model::FDE::data::mode{number}::neff", 
    }
    return result

def sweep_parameters(sim, paramater_name, para):
    # sim.newproject()
    # mode(fde)
    sim.addsweep(0)
    sim.setsweep("sweep", "name", paramater_name)
    sim.setsweep(paramater_name, "type", "Ranges")
    sim.setsweep(paramater_name, "number of points", 10)

    
    neff = []
    # define results
    for i in range(1, 5):
        neff.append(result_setup(f"neff{i}", i))
    sim.addsweepparameter(paramater_name, para)
    
    for i in range(1, 5):
        sim.addsweepresult(paramater_name, neff[i-1])

    sim.save(r"path")
    sim.runsweep(paramater_name)



def get_gap(sim):
        
    if os.path.exists("length_10_data.csv"):
        df_loaded = pd.read_csv('length_10_data.csv')

        # Access individual columns as Series or NumPy arrays
        distances_loaded = df_loaded['distances']
        lengths_loaded = df_loaded['Lengths']
        lengths_e_loaded = df_loaded['Lengths_e']

        # Or convert to NumPy arrays directly
        distances_np = df_loaded['distance'].to_numpy()
        lengths_np = df_loaded['length'].to_numpy()
        lengths_e_np = df_loaded['length_e'].to_numpy()
    else:

        sim.switchtolayout()
        sim.deleteall()
        print("Starting laying out geometry")
        array_geometry(sim,distance=2e-6,N_a=2)
        sim.addfde()
        sim.set("solver type", 1)
        sim.set("z", 0)
        sim.set("z span", 4e-6)
        sim.set("x", -0.1e-6)
        sim.set("y", 0)
        sim.set("y span", 10e-6)
        sim.set("define y mesh by", 1)
        sim.set("define z mesh by", 1)
        sim.set("dy", 0.02e-6)
        sim.set("dz", 0.02e-6)
        sim.save(filename_mode)
        Lengths=[]
        Lengths_e=[]

        distances=np.linspace(0.5,1,5)*1e-6

        for kk, d in enumerate(distances):
            n1=0
            n2=0
            n1_e=0
            n2_e=0
            for ii in range(2):
                #for non etched region
                sim.switchtolayout()
                sim.setnamed("geometry0::waveguide","y",2e-6-d)
                sim.setnamed("FDE","x",-0.1e-6)
                sim.run()
                sim.mesh()
                sim.findmodes()
                n1 = np.abs(sim.getresult("mode1", "neff"))
                n2 = np.abs(sim.getresult("mode2", "neff"))          

                sim.switchtolayout()
                sim.setnamed("FDE","x",0.1e-6)
                sim.run()
                sim.mesh()
                sim.findmodes()
                n1_e = np.abs(sim.getresult("mode1", "neff"))
                print(n1_e)
                n2_e = np.abs(sim.getresult("mode2", "neff"))
                print(n2_e)
            non_etched_delta_n=np.abs(n1.item()-n2.item())
            etched_delta_n=np.abs(n1_e.item()-n2_e.item())
            wavelength=1.550e-6
            Length_10=np.arcsin(np.sqrt(0.1))/(np.pi*non_etched_delta_n)*wavelength
            Length_10_e=np.arcsin(np.sqrt(0.1))/(np.pi*etched_delta_n)*wavelength
            print(Length_10)
            print(Length_10_e)

            Lengths.append(Length_10)
            Lengths_e.append(Length_10_e)
        df = pd.DataFrame({
            'distances': distances,
            'Lengths': Lengths,
            'Lengths_e': Lengths_e
        })

        # Optionally save to a CSV file
        df.to_csv('length_10_data.csv', index=False)


    plt.figure(figsize=(8, 6))

    # First curve: Tradeoff
    plt.plot(
        distances,
        Lengths,
        marker='o',
        label="Non-etched curve"
    )
    plt.plot(
        distances,
        Lengths_e,
        marker='o',
        label="Etched curve"
    )
    plt.xlabel("D")
    plt.ylabel("L_10")
    plt.title(f"Length_10%")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)

    # --- Enable interactive cursors ---
    # 'multiple=True' lets you select multiple data points and keep them visible
    cursor = mplcursors.cursor(multiple=True)

    # Customize annotation text
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target
        sel.annotation.set_text(f"K={x:.3f}\nAng_freq={y:.3f}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    plt.tight_layout()
    plt.show()

        

if __name__=="__main__":
    wavelengths=np.linspace(1.5,1.6,10)*1e-6
    get_gap(sim=lumapi.MODE(filename_mode))