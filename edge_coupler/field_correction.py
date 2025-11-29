from variables import *
from scipy.interpolate import RegularGridInterpolator

sim=lumapi.FDTD(filename_fdtd)
mname="FDTD::ports::input_port"


if os.path.exists("data/input_port_power_profile.npz"):
        data = np.load("data/input_port_power_profile.npz")
        PP_values = data["PP_values"]
        port_y = data["port_y"]
        port_z = data["port_z"]
else:
        P=sim.getresult(mname,'P')
        port_y=sim.getresult(mname,"y")
        port_z=sim.getresult(mname,"z")
        PP_values=P["P"]
        PP_values=PP_values[0,:,:,0,0]
        port_y=port_y[:,0]
        port_z=port_z[:,0]

        np.savez("data/input_port_power_profile", PP_values=PP_values, port_y=port_y,port_z=port_z)


filename="mode_edge_coupler"
sim=lumapi.MODE(filename)
mode_name='FDE::data::mode2'


if os.path.exists("data/mode_port_power_profile.npz"):
        data = np.load("data/mode_port_power_profile.npz")

        FP_values = data["FP_values"]
        fiber_y = data["fiber_y"]
        fiber_z= data["fiber_z"]
else:
        Fiber_P = sim.getresult(mode_name,'P')
        fiber_y= sim.getresult(mode_name,'y')
        fiber_z=sim.getresult(mode_name,'z')
        FP_values=Fiber_P["P"]
        FP_values=FP_values[0,:,:,0,0]
        fiber_y=fiber_y[:,0]
        fiber_z=fiber_z[:,0]
        np.savez("data/mode_port_power_profile", FP_values=FP_values, fiber_y=fiber_y,fiber_z=fiber_z)

Y2,Z2 = np.meshgrid(fiber_y, fiber_z, indexing='xy') 
interp = RegularGridInterpolator((port_y, port_z), PP_values,
                                 method='linear',
                                 bounds_error=False,
                                 fill_value=None)  # we'll clip coords before calling


# 2) Build list of target points (note the order: RegularGridInterpolator expects points as (z,y))
Y2_flat = Y2.ravel()
Z2_flat = Z2.ravel()  # shape (201*201,)

pts = np.vstack([Y2_flat, Z2_flat]).T  # shape (Npts, 2)

pts_clipped = pts.copy()
pts_clipped[:, 0] = np.clip(pts[:, 0], port_y.min(), port_y.max())  # clamp z
pts_clipped[:, 1] = np.clip(pts[:, 1], port_z.min(), port_z.max())  # clamp y


data1_on_201 = interp(pts_clipped).reshape(Z2.shape)  # shape (201,201)

outside = (
    (pts[:, 0] < port_y.min()) |
    (pts[:, 0] > port_y.max()) |
    (pts[:, 1] < port_z.min()) |
    (pts[:, 1] > port_z.max())
)

# Apply mask (reshape back to grid)
data1_on_201 = data1_on_201.reshape(-1)
data1_on_201[outside] = 0
data1_on_201 = data1_on_201.reshape(Z2.shape)

# Now data1_on_201 has the interpolated interior and constant boundary extension outside original z1/y1.

# --- Overlap calculation ---
# If fields may be complex, use conjugate on the first field.
dy = fiber_y[1] -fiber_y[0]
dz = fiber_z[1] -fiber_z[0]

area_element = dz * dy
overlap = np.sum(np.conjugate(data1_on_201) * FP_values) * area_element

norm1 = np.sum(np.abs(data1_on_201)**2) * area_element
norm2 = np.sum(np.abs(FP_values)**2) * area_element
overlap_norm = np.abs(overlap)**2 / (norm1 * norm2) if (norm1>0 and norm2>0) else 0.0

print("overlap =", overlap)
print("normalized overlap (|<f|g>|^2/(||f||^2||g||^2)) =", overlap_norm)

