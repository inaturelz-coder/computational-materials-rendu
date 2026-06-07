"""
m02_dft.py — 任脉第 1 步：DFT (电子尺度)

Demos:
  - Bulk-modulus fit via Birch-Murnaghan EOS (the classic DFT post-processing)
  - Mock band-gap from a fake DOS
  - Convergence-test helper (k-point + ENCUT scan style)

No real DFT engine here — uses synthetic data so it runs anywhere.
For real work see VASP / Quantum ESPRESSO / FHI-aims tutorials in 第二篇.
"""

import math
import numpy as np
from scipy.optimize import curve_fit

# ---------- Birch-Murnaghan 3rd-order EOS ----------
def birch_murnaghan(V, V0, E0, B0, Bp):
    """Energy as a function of volume; B0 in eV/Å³, V in Å³, E in eV."""
    eta = (V0 / V) ** (1.0 / 3.0)
    return E0 + 9 * V0 * B0 / 16.0 * (
        (eta**2 - 1) ** 3 * Bp
        + (eta**2 - 1) ** 2 * (6 - 4 * eta**2)
    )

def fit_eos(volumes, energies):
    """Fit BM3 EOS. Returns (V0_Å³, E0_eV, B0_GPa, Bp).
    1 eV/Å³ = 160.21766 GPa"""
    EV_A3_TO_GPA = 160.21766
    V0_guess = volumes[np.argmin(energies)]
    E0_guess = energies.min()
    p0 = (V0_guess, E0_guess, 1.0, 4.0)
    popt, _ = curve_fit(birch_murnaghan, volumes, energies, p0=p0, maxfev=20000)
    V0, E0, B0, Bp = popt
    return V0, E0, B0 * EV_A3_TO_GPA, Bp

# ---------- Mock DOS → band gap ----------
def band_gap_from_dos(energies, dos, tol=1e-3):
    """Find the gap = distance between highest occupied (dos>tol below E=0)
    and lowest unoccupied (dos>tol above E=0). Convention: E_F = 0."""
    occ_mask = (energies < 0) & (dos > tol)
    unocc_mask = (energies > 0) & (dos > tol)
    if not occ_mask.any() or not unocc_mask.any():
        return 0.0
    e_vbm = energies[occ_mask].max()
    e_cbm = energies[unocc_mask].min()
    return e_cbm - e_vbm

# ---------- Convergence-test helper ----------
def converged(values, threshold_per_atom_meV=1.0, n_atoms=1):
    """Return the smallest index k such that
    max |v[k:] - v[-1]| / n_atoms < threshold (meV)."""
    arr = np.asarray(values)
    diffs = np.abs(arr - arr[-1]) * 1000.0 / n_atoms  # meV/atom
    for k in range(len(arr)):
        if diffs[k:].max() < threshold_per_atom_meV:
            return k
    return len(arr) - 1

# ---------- Demo ----------
def demo():
    print("=== DFT post-processing demos ===\n")

    # 1) Bulk modulus fit (mock data near Cu's V0 ≈ 11.8 Å³/atom)
    V = np.linspace(10.5, 13.5, 9)
    truth = (11.8, -3.71, 0.95, 4.5)  # in eV/Å³ units
    np.random.seed(0)
    E_obs = birch_murnaghan(V, *truth) + np.random.normal(0, 1e-4, V.shape)
    V0, E0, B0_GPa, Bp = fit_eos(V, E_obs)
    print(f"BM3 fit:  V0={V0:.3f} Å³  E0={E0:.4f} eV  "
          f"B0={B0_GPa:.0f} GPa  B'={Bp:.2f}")
    print(f"  (truth:  V0={truth[0]}  B0={truth[2]*160.218:.0f} GPa  B'={truth[3]})\n")

    # 2) DOS → gap (mock silicon-like)
    E = np.linspace(-5, 5, 1000)
    dos_v = np.exp(-(E + 2.0)**2 / 0.5)   # valence peak at -2
    dos_c = np.exp(-(E - 1.1)**2 / 0.5)   # conduction peak at +1.1 (gap≈1.1)
    dos = (dos_v + dos_c) * (np.abs(E) > 0.45)  # forbidden zone
    print(f"DOS-extracted band gap: {band_gap_from_dos(E, dos):.3f} eV  (target 1.10 eV, Si)\n")

    # 3) Convergence scan (k-mesh from 4³ to 12³)
    k_grids = [4, 6, 8, 10, 12]
    E_per_atom = [-3.5630, -3.5712, -3.5740, -3.5745, -3.5746]
    k_idx = converged(E_per_atom, threshold_per_atom_meV=1.0, n_atoms=1)
    print(f"k-mesh converged at {k_grids[k_idx]}³ (within 1 meV/atom)")

if __name__ == '__main__':
    demo()
