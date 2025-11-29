import matplotlib.pyplot as plt
import numpy as np
import lumapi 
import math
import plotly.graph_objects as go 
import plotly.io as pio
import mplcursors
import numpy as np
import logging
import os


filename_mode="edge_coupler_mode"
filename_fdtd="fdtd_edge_coupler"

wavelength=1.55e-6
thick_Clad = 0.48e-6 # thickness of the top cladding layer
thick_Si = 0.22e-6 # thickness of the Si layer
thick_BOX = 2.0e-6 # thickness of the BOX layer
thick_Substrate=10e-6   #thickness of Substrate
width_Si = 0.8e-6 # width of the waveguide
material_Clad = "SiO2 (Glass) - Palik"
material_BOX = "SiO2 (Glass) - Palik"
material_Si = "Si (Silicon) - Palik"

SMF_28_cladd_index=1.434816
SMF_28_core_index=1.44


# define simulation region
width_margin = 2.0e-6; # space to include on the side of the waveguide
height_margin = 1.0e-6; # space to include above and below the waveguide


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
        sel.annotation.set_text(f"{x_label}={x:.3f}\{y_label}={y:.3f}")
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


def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger that appends to a file. Only create FileHandler once."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Only add handler if the logger has no handlers yet
    if not logger.handlers:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True) if os.path.dirname(log_file) else None
        
        fh = logging.FileHandler(log_file, mode='a')  # append mode
        fh.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger
