import matplotlib.pyplot as plt
import numpy as np
import lumapi 
import math
import plotly.graph_objects as go 
import plotly.io as pio
import mplcursors
import numpy as np


filename_mode="wga_mode"
filename_fdtd="wga_fdtd"

thick_Clad = 0.48e-6 # thickness of the top cladding layer
thick_Si = 0.12e-6 # thickness of the Si layer
thick_BOX = 2.0e-6 # thickness of the BOX layer
width_Si = 0.8e-6 # width of the waveguide
N = 50 # number of grating periods
l_g = 0.64e-6 # length of the grating period
dc = 0.6 # duty cycle of the grating
t_r = 0.08e-6 # thickness of the gap between the grating teeth and the core
t_g = thick_Clad - t_r # thickness of the grating teeth
l = N* l_g # total length of the waveguide
# define materials
material_Clad = "SiO2 (Glass) - Palik"
material_BOX = "SiO2 (Glass) - Palik"
material_Si = "Si (Silicon) - Palik"

# define simulation region
width_margin = 2.0e-6; # space to include on the side of the waveguide
height_margin = 1.0e-6; # space to include above and below the waveguide

# calculate simulation volume
# propagation in the x-axis direction; z-axis is wafer-normal
Xmin = -l/2-10e-6
Xmax = l/2+10e-6 # length of the waveguide
Zmin = -height_margin
Zmax = thick_Si + height_margin
Y_span = 2*width_margin + width_Si
Ymin = -Y_span/2
Ymax = -Ymin




def plot(Num_v,x,variables,labels,x_label,y_label,graph_label):
    plt.figure(figsize=(8, 6))
    for var, label in zip(variables, labels):
    # First curve: Tradeoff
        plt.plot(
            x,
            var,
            marker='o',
            label=label
        )
    # Labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(graph_label)
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)

    # --- Enable interactive cursors ---
    # 'multiple=True' lets you select multiple data points and keep them visible
    cursor = mplcursors.cursor(multiple=True)

    # Customize annotation text
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target
        sel.annotation.set_text(f"K={x:.3f}\nAng_wavelengths={y:.3f}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    plt.tight_layout()
    plt.show()



def colorplot(x,y,F,x_label,y_label,graph_tiltle):
    # Create meshgrid for 2D data
    # Handle 3D input (multiple frequency slices)    
    # Create heatmap using plotly
    fig = go.Figure(data=go.Heatmap(z=np.abs(F).T, x=x, y=y, colorscale='jet'))
    
    fig.update_layout(
        title=graph_tiltle,
        xaxis_title=x_label,
        yaxis_title=y_label,
        width=800,
        height=600
    )
    
    fig.show()

def plot_fft(x,y,F,x_label,y_label,graph_tiltle):
    # Create meshgrid for 3D plot
    X, Y = np.meshgrid(x, y)  # Note:   Y corresponds to x-axis, X corresponds to y-axis
    
    # Handle 3D input (multiple frequency slices)
    if len(F.shape) == 3:
        # Sum over all frequencies or take magnitude
        F_plot = np.abs(F[:,:,0])  # Use first frequency slice
    else:
        F_plot = np.abs(F)
    
    # Create 3D surface plot using plotly
    fig = go.Figure(data=[go.Surface(z=F_plot.T, x=X, y=Y, colorscale='jet')])
    
    fig.update_layout(
        title=graph_tiltle,
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title='|FFT|',
            aspectmode='cube'
        )
    )
    
    fig.show()
