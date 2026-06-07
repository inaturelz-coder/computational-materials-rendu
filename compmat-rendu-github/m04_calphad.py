"""
m06_cpfem.py — 任脉第 5 步：CP-FEM (连续力学)

Demos:
  - Schmid factor for a slip system (single crystal)
  - Voigt / Reuss / Hill polycrystal averaging of elastic moduli
  - Yield surface (Mises vs Tresca) for a 2-D plane-stress sweep
"""

import numpy as np

# ---------- Schmid factor ----------
def schmid_factor(n_slip, b_slip, stress_axis):
    """Resolved shear stress per unit applied stress: m = (n·σ̂)(b·σ̂).
    n_slip: slip-plane normal (unit), b_slip: slip direction (unit),
    stress_axis: tensile direction (unit)."""
    n = np.asarray(n_slip, dtype=float); n /= np.linalg.norm(n)
    b = np.asarray(b_slip, dtype=float); b /= np.linalg.norm(b)
    s = np.asarray(stress_axis, dtype=float); s /= np.linalg.norm(s)
    return abs(np.dot(n, s) * np.dot(b, s))

# ---------- Polycrystal averaging ----------
def voigt_reuss_hill(C):
    """Voigt-Reuss-Hill bounds on isotropic G, K from cubic elastic constants C11, C12, C44.
    Pass C as dict {'C11':..., 'C12':..., 'C44':...} in same units (e.g. GPa)."""
    C11, C12, C44 = C['C11'], C['C12'], C['C44']
    # Voigt bounds
    K_V = (C11 + 2 * C12) / 3
    G_V = (C11 - C12 + 3 * C44) / 5
    # Reuss bounds (cubic crystals)
    K_R = K_V
    G_R = 5 * (C11 - C12) * C44 / (4 * C44 + 3 * (C11 - C12))
    # Hill = arithmetic mean
    K_H = 0.5 * (K_V + K_R)
    G_H = 0.5 * (G_V + G_R)
    # Young's & Poisson from K, G
    E = 9 * K_H * G_H / (3 * K_H + G_H)
    nu = (3 * K_H - 2 * G_H) / (2 * (3 * K_H + G_H))
    return {'K_VRH': K_H, 'G_VRH': G_H, 'E_VRH': E, 'nu_VRH': nu,
            'K_V': K_V, 'G_V': G_V, 'K_R': K_R, 'G_R': G_R}

# ---------- Yield surfaces in plane stress ----------
def mises_yield(sigma_x, sigma_y, sigma_xy=0.0):
    """von Mises equivalent stress for plane stress."""
    return np.sqrt(sigma_x**2 + sigma_y**2 - sigma_x*sigma_y + 3*sigma_xy**2)

def tresca_yield(sigma_x, sigma_y, sigma_xy=0.0):
    """Tresca = max principal stress difference."""
    R = 0.5 * np.sqrt((sigma_x - sigma_y)**2 + 4*sigma_xy**2)
    p1 = 0.5 * (sigma_x + sigma_y) + R
    p3 = 0.5 * (sigma_x + sigma_y) - R
    return p1 - p3

# ---------- Demo ----------
def demo():
    print("=== CP-FEM building blocks ===\n")

    # Schmid factor: fcc (111)[1̄01] slip vs <100> tensile
    m = schmid_factor([1,1,1], [-1,0,1], [1,0,0])
    print(f"Schmid factor (111)[1̄01] under <100> tension = {m:.3f}  (expected 0.408)")

    # VRH: Cu cubic elastic constants (GPa)
    cu = {'C11': 169, 'C12': 122, 'C44': 75}
    res = voigt_reuss_hill(cu)
    print(f"\nCu polycrystal (from C_ij in GPa):")
    print(f"  K_VRH = {res['K_VRH']:.0f} GPa   (expt ≈ 140)")
    print(f"  G_VRH = {res['G_VRH']:.0f} GPa   (expt ≈  48)")
    print(f"  E_VRH = {res['E_VRH']:.0f} GPa   (expt ≈ 130)")
    print(f"  ν_VRH = {res['nu_VRH']:.3f}     (expt ≈ 0.34)")

    # Yield surface sweep
    print("\nYield comparison at 45° biaxial (σx=σy=σ, σxy=0):")
    print(f"  Mises = {mises_yield(1,1):.3f} σ_y     Tresca = {tresca_yield(1,1):.3f} σ_y")
    print("Yield comparison at pure shear (σx=σ, σy=-σ, σxy=0):")
    print(f"  Mises = {mises_yield(1,-1):.3f} σ_y    Tresca = {tresca_yield(1,-1):.3f} σ_y")

if __name__ == '__main__':
    demo()
