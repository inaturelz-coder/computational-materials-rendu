"""
m11_icme.py — 两脉交汇：ICME 完整闭环 (mini-demo)

This script wires together cheap surrogates of every previous stage:
   DFT (m02) -> CALPHAD (m04) -> Phase-field (m05) -> CP-FEM (m06)
   wrapped in a BO loop (m08) that uses UQ (m09) for decision-making.

It is not a real ICME pipeline — it is a runnable demo of the data flow.
"""

import numpy as np
from m02_dft import birch_murnaghan, fit_eos
from m04_calphad import G_regular, critical_T
from m05_phasefield import cahn_hilliard_1d, domain_size
from m06_cpfem import voigt_reuss_hill, mises_yield
from m07_ml import GP
from m08_bo import expected_improvement
from m09_uq import mc_forward, percentile_ci

def proxy_dft(composition_x):
    """Surrogate DFT: returns elastic modulus from composition (cheap polynomial)."""
    # Cubic alloy: stiffer at intermediate composition, softer at endpoints
    C11 = 150 + 80 * np.sin(np.pi * composition_x)     # GPa
    C12 = 100 + 30 * np.sin(np.pi * composition_x)
    C44 = 60 + 25 * np.sin(np.pi * composition_x)
    return {'C11': C11, 'C12': C12, 'C44': C44}

def proxy_calphad(composition_x, T=1000):
    """Surrogate CALPHAD: Gibbs energy + spinodal flag."""
    omega = 25000 * (1 + 0.2 * composition_x)           # J/mol
    G = G_regular(composition_x, T, omega)
    Tc = critical_T(omega)
    in_spinodal = T < Tc
    return {'G': G, 'T_c': Tc, 'spinodal': in_spinodal}

def proxy_phasefield(composition_x, n_steps=2000):
    """Surrogate Phase-field: domain size as proxy for microstructure."""
    snaps = cahn_hilliard_1d(N=128, L=32, n_steps=n_steps, dt=0.05,
                             c0=composition_x, noise=0.05, seed=int(composition_x*1000))
    Lc = domain_size(snaps[-1], 32/128)
    return {'domain_size': Lc}

def proxy_yield(composition_x):
    """Proxy yield stress from polycrystal averaging + microstructure factor."""
    elastic = proxy_dft(composition_x)
    vrh = voigt_reuss_hill(elastic)
    G = vrh['G_VRH']
    pf = proxy_phasefield(composition_x, n_steps=1500)
    # Hall-Petch-like: smaller domain → stronger
    sigma_y = 0.005 * G * 1000 + 50 / max(pf['domain_size'], 1.0)
    return sigma_y

def icme_objective(x):
    """Single composition → final property: yield stress (MPa)."""
    if x < 0 or x > 1:
        return -1e9
    return proxy_yield(x)

# ---------- Mini-BO loop over composition ----------
def icme_bo(n_init=3, n_iter=5, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.1, 0.9, n_init).reshape(-1, 1)
    y = np.array([icme_objective(float(x)) for x in X.ravel()])
    print(f"Initial: best = {y.max():.1f} MPa @ x = {float(X[y.argmax()]):.3f}\n")

    for it in range(n_iter):
        gp = GP(length=0.2, sigma_f=20.0, sigma_n=1.0).fit(X, y)
        X_cand = np.linspace(0.05, 0.95, 100).reshape(-1, 1)
        mu, std = gp.predict(X_cand)
        ei = expected_improvement(mu, std, y.max(), xi=1.0)
        x_new = X_cand[np.argmax(ei)]
        y_new = icme_objective(float(x_new[0]))
        X = np.vstack([X, x_new]); y = np.append(y, y_new)
        print(f"  iter {it+1}: x={float(x_new[0]):.3f}, "
              f"yield={y_new:.1f} MPa, best={y.max():.1f} MPa")
    return X, y

# ---------- UQ wrapper on the optimum ----------
def icme_uq(x_opt, n_mc=50):
    """Sample uncertain composition around x_opt, propagate to yield stress."""
    def sampler(N): return np.random.default_rng(7).normal(x_opt, 0.02, (N, 1))
    Y = mc_forward(lambda x: icme_objective(float(x[0])), sampler, n_mc=n_mc)
    lo, hi = percentile_ci(Y)
    return {'mean': Y.mean(), 'std': Y.std(), 'ci_95': (lo, hi)}

# ---------- Demo ----------
def demo():
    print("=== ICME mini-demo: composition → properties via 5-stage chain ===\n")
    print("Stage 1 (DFT):       elastic constants from composition")
    print("Stage 2 (CALPHAD):   Gibbs energy + spinodal")
    print("Stage 3 (PF):        microstructure (domain size)")
    print("Stage 4 (CP-FEM):    polycrystal yield stress")
    print("Stage 5 (BO + UQ):   wrap stages 1-4, find composition that maximizes yield\n")

    print("--- Running BO loop ---")
    X, y = icme_bo(n_init=3, n_iter=4, seed=2)
    x_opt = float(X[y.argmax()][0])
    print(f"\nFinal optimum: x = {x_opt:.3f}, yield = {y.max():.1f} MPa")

    print("\n--- UQ on optimum (composition uncertainty ±0.02) ---")
    uq = icme_uq(x_opt, n_mc=20)
    print(f"  yield = {uq['mean']:.1f} ± {uq['std']:.1f} MPa  "
          f"95% CI = [{uq['ci_95'][0]:.1f}, {uq['ci_95'][1]:.1f}]")

if __name__ == '__main__':
    demo()
