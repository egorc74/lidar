import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
import mplcursors
import ast 

###Draw dispersion w-K relation
#function to extract w value for a given cos(2*pi*K/g)


A= 0.64e-6 # length of the grating period
dc = 0.6 # duty cycle of the grating
d1=A*dc
d2=A*(1-dc)
c_0=3e8
g=2*np.pi/A

n1=2.139146
n2=2.156307
N_AVG=(n1*d1+n2*d2)/A


def num_invert(f,cos_value,bracket):
    fi=f(bracket[0])-cos_value
    fs=f(bracket[1])-cos_value
    if(fs*fi<0):
        sol=root_scalar(lambda x: f(x) - cos_value , bracket=bracket)
        return sol.root
    return np.nan


def get_cos_value(K,g):
    v=np.cos(2*np.pi*K/g)
    return v
def f(w):
    delta=(n1*d1-n2*d2)/(n1*d1+n2*d2)
    cos_value=1/(4*n1*n2)*(np.cos(np.pi*w/w_bragg)*(n1+n2)**2 -np.cos(np.pi*w/w_bragg*delta)*(n2-n1)**2) 
    return cos_value

w_first_order=[]
w_second_order=[]
w_third_order=[]

K_values = []
w_bragg_values_1=[]
w_bragg_values_2=[]


K_values=np.linspace(0,g,1000)
C=c_0/N_AVG


for i, K in enumerate(K_values):
    w_bragg=np.pi*C/A
    w_bragg_values_1.append(w_bragg)
    w_bragg_values_2.append(2*w_bragg)    
    
    cos_value=get_cos_value(K,g)
    W_1=num_invert(lambda w: f(w), cos_value=cos_value , bracket=[0,w_bragg])
    w_first_order.append(W_1)

    W_2=num_invert(lambda w: f(w), cos_value=cos_value , bracket=[w_bragg,2*w_bragg])
    w_second_order.append(W_2)
    
    W_3=num_invert(lambda w: f(w), cos_value=cos_value , bracket=[2*w_bragg,3*w_bragg])
    w_third_order.append(W_3)

    #light line 
    w_homo=C*K

print(g)
light_line=c_0/N_AVG*np.array(K_values)


#calculate bandgap in wavelength
wavelength_1=c_0/w_second_order[len(K_values)-1]*2*np.pi
wavelength_2=c_0/w_third_order[len(K_values)-1]*2*np.pi

print(np.abs(wavelength_1-wavelength_2))
print(f"cuttoff wavelength_1: {wavelength_1}")
print(f"cuttoff wavelength_2: {wavelength_2}")









plt.figure(figsize=(8, 6))

# First curve: Tradeoff
plt.plot(
    K_values,
    w_first_order,
    marker='o',
    label="First Order Bloch mode"
)

# Second curve: Transmission
plt.plot(
    K_values,
    w_second_order,
    marker='o',
    label=f"Second order Bloch mode"
)
plt.plot(
    K_values,
    w_third_order,
    marker='o',
    label=f"Third order Bloch mode"
)
plt.plot(
    K_values,
    w_bragg_values_1,
    marker='o', 
    label=f"Bandgap"
)
plt.plot(
    K_values,
    w_bragg_values_2,
    marker='o', 
    label=f"Second Bandgap"
)
plt.plot(
    K_values,
    light_line,
    linestyle='--', 
    label=f"Light line"
)
# Labels and title
plt.xlabel("K")
plt.ylabel("W")
plt.title(f"Dispersion diagam")
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













