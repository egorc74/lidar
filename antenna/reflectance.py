import math
import numpy as np
import matplotlib.pyplot as plt
def calculate_reflection(n_a,n_b,incident_angle=0):
    reflection=(n_a*np.cos(incident_angle)-n_b*np.cos(incident_angle))/(n_a*np.cos(incident_angle)+n_b*np.cos(incident_angle))      #correct reflection from b to a
    return reflection

def calculate_reflection_phase(wavelength,thickness,refractive_index,incident_angle=0):
    phase=2*thickness*2*np.pi*refractive_index/wavelength
    return phase

def calculate_full_reflection_for_4_layer_structure(wavelength,thickness_1=0,thickness_2=0,thickness_3=0,thickness_4=0,n_a=0,n_b=0,incident_angle=0):
    r_3_4=calculate_reflection(n_a=n_a,n_b=n_b)
    r_2_3=calculate_reflection(n_a=n_b,n_b=n_a)
    r_1_2=calculate_reflection(n_a=n_a,n_b=n_b)
    phase_3_4=calculate_reflection_phase(wavelength=wavelength,thickness=thickness_3,refractive_index=n_a)
    phase_2_3=calculate_reflection_phase(wavelength=wavelength,thickness=thickness_2,refractive_index=n_b)
      
    reflection_w_b=(r_3_4 * np.exp(-1j*phase_3_4)+r_2_3)/(1+r_2_3*r_3_4*np.exp(-1j*phase_3_4))
    reflection_full=(reflection_w_b * np.exp(-1j*phase_2_3)+r_1_2)/(1+r_1_2*reflection_w_b*np.exp(-1j*phase_2_3))
    return reflection_full , phase_2_3 

wave_length=1.55*1e-6
thickness_Si_span=np.linspace(0,1,200)*1e-6
thickness_Box=3*1e-6    # by setting this in to 3um the results are obtained that are described in paper 
n_Si=3.475
n_SiO2=1.444

reflectance_array=np.zeros(len(thickness_Si_span))
phase_array=np.zeros(len(thickness_Si_span))

for i in range(len(thickness_Si_span)):
    reflection, phase = calculate_full_reflection_for_4_layer_structure(
        wavelength=wave_length,
        thickness_2=thickness_Si_span[i],
        thickness_3=thickness_Box,
        n_a=n_SiO2,
        n_b=n_Si
    )
    reflectance_array[i] = np.abs(reflection)**2
    phase_array[i] = phase

reflectance_array = np.array(reflectance_array)  # convert to NumPy array
max_value = np.max(reflectance_array)
max_index = np.argmax(reflectance_array)
max_thickness = thickness_Si_span[max_index]
print(max_value)

print(max_thickness)

fig, ax1 = plt.subplots()

# Left y-axis: Reflectance
ax1.plot(thickness_Si_span, reflectance_array, 'b-', label='Reflectance')
ax1.set_xlabel('Si thickness (nm)')
ax1.set_ylabel('Reflectance', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Right y-axis: Phase
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(thickness_Si_span, phase_array, 'r--', label='Phase')
ax2.set_ylabel('Phase (degrees)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Optional: grid only for left axis
ax1.grid(True)

# Optional: combine legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')

plt.title('Reflectance and Phase vs Si Thickness')
plt.show()