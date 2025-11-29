import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
import mplcursors
import ast 

###Draw dispersion w-K relation
#function to extract w value for a given cos(2*pi*K/g)


A= 0.66e-6 # length of the grating period
dc = 0.5 # duty cycle of the grating
d1=A*dc
d2=A*(1-dc)
c_0=3e8
g=2*np.pi/A

refractive_indices = pd.read_csv('refractive_indices.csv')

def extract_number(cell):
    try:
        # Convert string like '[[2.29204303+0.j]]' → nested Python list [[2.29204303+0j]]
        val = ast.literal_eval(cell)
        # Return the scalar inside nested list
        return complex(val[0][0])
    except Exception:
        return float('nan')
    

refractive_indices['n1'] = refractive_indices['n1'].apply(extract_number)
refractive_indices['n2'] = refractive_indices['n2'].apply(extract_number)



print(refractive_indices.dtypes)
print(refractive_indices.head())

wavelengths = refractive_indices['wavelength']
n1_eff = np.abs(refractive_indices['n1'].to_numpy())
n2_eff = np.abs(refractive_indices['n2'].to_numpy())


N_AVG_0=(n2_eff[len(n2_eff)-1]*d2+n1_eff[len(n1_eff)-1]*d1)/A
N_AVG=(n2_eff[int(len(n2_eff)/2)-1]*d2+n1_eff[int(len(n1_eff)/2)-1]*d1)/A

print(f"wavelengths: {wavelengths}")
print(f"n1: {n1_eff}")
print(f"n2: {n2_eff}")

def num_invert(f,cos_value,bracket):
    sol=root_scalar(lambda x: f(x) - cos_value , bracket=bracket)
    return sol.root


def find_root(f, cos_value, w_start, w_end, steps=1000):
    ws = np.linspace(w_start, w_end, steps)
    fs = f(ws) - cos_value
    for i in range(len(ws)-1):
        if fs[i] * fs[i+1] < 0:
            sol = root_scalar(lambda w: f(w) - cos_value, bracket=[ws[i], ws[i+1]])
            return sol.root
    print(f"nan value was inserted")
    return np.nan

def get_cos_value(K,g):
    v=np.cos(2*np.pi*K/g)
    return v
def f(w,n1,n2,w_bragg):
    delta=(n1*d1-n2*d2)/(n1*d1+n2*d2)
    cos_value=1/(4*n1*n2)*((n1+n2)**2*np.cos(np.pi*w/w_bragg)-(n2-n1)**2*np.cos(w*np.pi/w_bragg*delta)) 
    return cos_value

w_first_order=[]
w_second_order=[]
w_third_order=[]

K_values = []
w_bragg_values_1=[]
w_bragg_values_2=[]

c_values=[]

for i, wl in enumerate(wavelengths):
    n1=np.abs(n1_eff[i])
    n2=np.abs(n2_eff[i])
    n_avg=(n1*d1+n2*d2)/A
    C=c_0/n_avg
    c_values.append(C)
    w_bragg=np.pi*C/A
    w_bragg_values_1.append(w_bragg)
    w_bragg_values_2.append(2*w_bragg)

    K0=2*np.pi/wavelengths[len(wavelengths)-1]*N_AVG_0
    K=2*np.pi/wl*n_avg-K0
    
    K_values.append(K)
    cos_value=get_cos_value(K,g)
    W_1=find_root(lambda w: f(w, n1, n2, w_bragg), cos_value=cos_value , w_start=0,w_end=w_bragg,steps=1000)
    w_first_order.append(W_1)

    # W_2=num_invert(lambda w: f(w, n1, n2, w_bragg), cos_value=cos_value , bracket=[w_bragg,2*w_bragg])
    W_2=find_root(lambda w: f(w, n1, n2, w_bragg), cos_value=cos_value , w_start=w_bragg,w_end=2*w_bragg,steps=1000)
    w_second_order.append(W_2)
    
    W_3=num_invert(lambda w: f(w, n1, n2, w_bragg), cos_value=cos_value , bracket=[2*w_bragg,3*w_bragg])
    w_third_order.append(W_3)

    #light line 
    w_homo=C*K

print(g)
light_line=c_0/N_AVG*np.array(K_values)





wavelength_1=c_0/w_second_order[len(wavelengths)-1]*2*np.pi
wavelength_2=c_0/w_third_order[len(wavelengths)-1]*2*np.pi

print(np.abs(wavelength_1-wavelength_2))
print(f"cuttoff wavelength_1: {wavelength_1}")
print(f"cuttoff wavelength_2: {wavelength_2}")



wavelength_mean=c_0/np.median(w_second_order)*2*np.pi

print(f"mean second order bragg wavelength: {wavelength_mean}")









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











