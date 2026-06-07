"""
m09_uq.py — 督脉第 4 阶段：UQ (不确定性量化)

Demos:
  - MC forward propagation: x ~ p(x) → y = g(x) → distribution of y
  - Bootstrap confidence interval for a regression coefficient
  - Sobol global sensitivity (Saltelli decomposition, simple 2-input case)
"""

import numpy as np

# ---------- Monte Carlo forward propagation ----------
def mc_forward(g, sampler, n_mc=10_000):
    """g: deterministic function R^d → R; sampler: returns (n_mc, d) array."""
    X = sampler(n_mc)
    Y = np.array([g(x) for x in X])
    return Y

def percentile_ci(samples, alpha=0.05):
    """[lo, hi] = central (1-alpha) interval."""
    lo = np.percentile(samples, 100 * alpha / 2)
    hi = np.percentile(samples, 100 * (1 - alpha / 2))
    return lo, hi

# ---------- Bootstrap CI for OLS slope ----------
def bootstrap_slope(x, y, n_boot=2000, seed=0):
    """Bootstrap 95% CI on slope of y = a + b x."""
    rng = np.random.default_rng(seed)
    N = len(x)
    slopes = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, N, N)
        xb, yb = x[idx], y[idx]
        b = np.polyfit(xb, yb, 1)[0]
        slopes[i] = b
    return slopes.mean(), percentile_ci(slopes)

# ---------- Sobol indices (variance-based) ----------
def sobol_2d(f, n=2048, seed=0):
    """Approximate first-order Sobol indices for f(x1, x2) on [0,1]²."""
    rng = np.random.default_rng(seed)
    A = rng.random((n, 2))
    B = rng.random((n, 2))
    # Switch matrix C_i: A with column i replaced by B's column i
    C1 = A.copy(); C1[:, 0] = B[:, 0]
    C2 = A.copy(); C2[:, 1] = B[:, 1]
    yA = np.array([f(*x) for x in A])
    yB = np.array([f(*x) for x in B])
    yC1 = np.array([f(*x) for x in C1])
    yC2 = np.array([f(*x) for x in C2])
    var_total = np.var(np.concatenate([yA, yB]))
    S1 = np.mean(yB * (yC1 - yA)) / var_total
    S2 = np.mean(yB * (yC2 - yA)) / var_total
    return {'S1': S1, 'S2': S2, 'V_total': var_total}

# ---------- Demo ----------
def demo():
    print("=== UQ — forward MC propagation ===\n")
    # Forward: yield stress σ_y = K · ε^n with uncertain K, n
    def sampler(N):
        K = np.random.default_rng(1).normal(500, 30, N)   # MPa
        n = np.random.default_rng(2).normal(0.25, 0.03, N)
        return np.column_stack([K, n])
    def stress(KN, eps=0.05):
        K, n = KN
        return K * eps ** n
    Y = mc_forward(stress, sampler)
    lo, hi = percentile_ci(Y)
    print(f"σ_y at ε=0.05:  mean = {Y.mean():.1f} MPa,  95% CI = [{lo:.1f}, {hi:.1f}]")

    print("\n=== Bootstrap CI on regression slope ===\n")
    rng = np.random.default_rng(3)
    x = np.linspace(0, 10, 30)
    y = 2.5 * x + 1 + rng.normal(0, 1.5, 30)
    mean_b, ci = bootstrap_slope(x, y)
    print(f"slope = {mean_b:.3f}  95% CI = [{ci[0]:.3f}, {ci[1]:.3f}]  (truth 2.5)")

    print("\n=== Sobol indices ===\n")
    def f(x1, x2): return x1 ** 2 + 0.1 * x2     # x1 dominates
    s = sobol_2d(f, n=2048)
    print(f"S1 (x1) = {s['S1']:.2f}   S2 (x2) = {s['S2']:.2f}")
    print("→ S1 ≫ S2  means x1 dominates the output variance.")

if __name__ == '__main__':
    demo()
