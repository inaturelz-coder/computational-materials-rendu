"""
m04_calphad.py — 任脉第 3 步：CALPHAD (热力学)

Demos:
  - Regular solution Gibbs energy G(x, T)
  - Common-tangent miscibility gap (binary spinodal/coex curve)
  - Simple Redlich-Kister excess
"""

import numpy as np
from scipy.optimize import brentq

R = 8.314  # J/(mol·K)

def G_regular(x, T, omega):
    """Regular solution: G = R T (x ln x + (1-x) ln(1-x)) + omega x (1-x)"""
    eps = 1e-12
    x = np.clip(x, eps, 1 - eps)
    return R * T * (x * np.log(x) + (1 - x) * np.log(1 - x)) + omega * x * (1 - x)

def d2G_dx2(x, T, omega):
    """Curvature; spinodal where d²G/dx² = 0."""
    x = np.clip(x, 1e-9, 1 - 1e-9)
    return R * T * (1 / x + 1 / (1 - x)) - 2 * omega

def spinodal(T, omega):
    """Return (x_left, x_right) spinodal points where d²G/dx²=0; or None if 1 phase."""
    if d2G_dx2(0.5, T, omega) > 0:
        return None
    x_left = brentq(d2G_dx2, 1e-4, 0.5, args=(T, omega))
    x_right = brentq(d2G_dx2, 0.5, 1 - 1e-4, args=(T, omega))
    return x_left, x_right

def critical_T(omega):
    """T_c for regular solution = omega / (2 R)."""
    return omega / (2 * R)

# ---------- Redlich-Kister excess ----------
def rk_excess(x, T, L_params):
    """RK polynomial: G^xs = x(1-x) Σ_k L_k (1-2x)^k, L_k may depend on T.
    L_params: list of L_k (constants here)."""
    x = np.asarray(x)
    s = sum(L * (1 - 2 * x) ** k for k, L in enumerate(L_params))
    return x * (1 - x) * s

def G_rk(x, T, L_params):
    """Full Gibbs energy with RK excess (ideal mixing + RK)."""
    eps = 1e-12
    xc = np.clip(x, eps, 1 - eps)
    return R * T * (xc * np.log(xc) + (1 - xc) * np.log(1 - xc)) + rk_excess(x, T, L_params)

# ---------- Common-tangent via direct search ----------
def common_tangent(T, omega, x_grid=None):
    """Find binodal (coex) compositions for regular solution."""
    if x_grid is None:
        x_grid = np.linspace(1e-3, 1 - 1e-3, 401)
    G = G_regular(x_grid, T, omega)
    # Convex hull lower envelope = common tangent
    from scipy.spatial import ConvexHull
    pts = np.column_stack([x_grid, G])
    hull = ConvexHull(pts)
    lower = []
    for s in hull.simplices:
        if pts[s].mean(0)[1] < G.max():
            lower.extend(s)
    idx = sorted(set(lower))
    return x_grid[idx], G[idx]

# ---------- Demo ----------
def demo():
    print("=== CALPHAD regular-solution demo ===\n")
    omega = 20000  # J/mol  → T_c ≈ 1203 K
    print(f"omega = {omega} J/mol  →  T_c = {critical_T(omega):.0f} K\n")

    for T in [800, 1000, 1200, 1400]:
        sp = spinodal(T, omega)
        if sp is None:
            print(f"  T = {T} K: single phase (no spinodal)")
        else:
            print(f"  T = {T} K: spinodal at x = ({sp[0]:.3f}, {sp[1]:.3f})")

    # RK excess (mock Cu-Ag-like positive deviation)
    print("\nRK excess at x=0.5, T=1000 K (L0=15000, L1=2000, L2=-500):")
    print(f"  G_xs = {rk_excess(0.5, 1000, [15000, 2000, -500]):.0f} J/mol")

if __name__ == '__main__':
    demo()
