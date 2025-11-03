from fdtd_simulation import *
import mplcursors

def current_coupling(sim):
    T1 = sim.getdata("forward_m","T").flatten()
    T2 = sim.getdata("second_forward_m","T").flatten()
    Freq = sim.getdata("second_forward_m","f").flatten()
    c_0=3e8
    wavelengths=c_0/Freq

    plt.figure(figsize=(8, 6))

    # First curve: Tradeoff
    plt.plot(
        wavelengths,
        T1,
        marker='o',
        label="Main transmission"
    )

    # Second curve: Transmission
    plt.plot(
        wavelengths,
        T2,
        marker='o',
        label=f"Coupling transmission"
    )
    # Labels and title
    plt.xlabel("wavelengthsgth")
    plt.ylabel("Trans")
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
        sel.annotation.set_text(f"K={x:.3f}\nAng_wavelengths={y:.3f}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    plt.tight_layout()
    plt.show()

