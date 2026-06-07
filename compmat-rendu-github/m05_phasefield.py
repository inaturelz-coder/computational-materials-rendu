"""
m08_bo.py — 督脉第 3 阶段：Bayesian Optimization + MC

Demos:
  - Expected-Improvement (EI) acquisition
  - BO loop on 1-D toy "alloy property" function
  - Metropolis-Hastings sampler (for MCMC posterior on a parameter)
"""

import numpy as np
from m07_ml import GP, rbf

# ---------- Expected Improvement ----------
def expected_improvement(mu, std, y_best, xi=0.01):
    """EI for maximization: E[max(f - y_best - xi, 0)] under N(μ, σ)."""
    from scipy.stats import norm
    s = np.maximum(std, 1e-12)
    z = (mu - y_best - xi) / s
    ei = (mu - y_best - xi) * norm.cdf(z) + s * norm.pdf(z)
    ei[std < 1e-12] = 0.0
    return ei

# ---------- BO loop ----------
def bo_loop(f, bounds, n_init=4, n_iter=10, seed=0):
    """Run BO maximizing scalar f over [lo, hi]."""
    rng = np.random.default_rng(seed)
    lo, hi = bounds
    X = rng.uniform(lo, hi, size=(n_init, 1))
    y = np.array([f(float(x)) for x in X.ravel()])
    print(f"Initial best: y = {y.max():.3f} at x = {X[y.argmax()][0]:.3f}")

    for it in range(n_iter):
        gp = GP(length=(hi-lo)*0.15, sigma_f=1.0, sigma_n=1e-3).fit(X, y)
        # Acquisition grid search
        X_cand = np.linspace(lo, hi, 200).reshape(-1, 1)
        mu, std = gp.predict(X_cand)
        ei = expected_improvement(mu, std, y.max())
        x_new = X_cand[np.argmax(ei)]
        y_new = f(float(x_new[0]))
        X = np.vstack([X, x_new])
        y = np.append(y, y_new)
        print(f"  iter {it+1:2d}: queried x={float(x_new[0]):.3f}, y={y_new:.3f}, "
              f"best={y.max():.3f}")
    return X, y

# ---------- Metropolis-Hastings ----------
def metropolis_hastings(log_post, x0, n_steps=5000, step_size=0.5, seed=0):
    """Random-walk MH sampler for 1-D parameter."""
    rng = np.random.default_rng(seed)
    x = float(x0)
    samples = np.empty(n_steps)
    log_p_x = log_post(x)
    accepts = 0
    for i in range(n_steps):
        x_prop = x + rng.normal(0, step_size)
        log_p_prop = log_post(x_prop)
        if np.log(rng.random()) < log_p_prop - log_p_x:
            x, log_p_x = x_prop, log_p_prop
            accepts += 1
        samples[i] = x
    return samples, accepts / n_steps

# ---------- Demo ----------
def demo():
    print("=== Bayesian Optimization on toy alloy property ===\n")
    # Toy objective: e.g. tensile strength vs alloying fraction
    def f(x):
        return -(x - 0.7) ** 2 + 0.3 * np.sin(15 * x) + 1.0
    X, y = bo_loop(f, bounds=(0, 1), n_init=3, n_iter=8, seed=1)
    print(f"\nFinal best x = {X[y.argmax()][0]:.3f}  (true argmax ≈ 0.70)")

    print("\n=== MCMC sampling toy posterior ===\n")
    # Posterior: log p(θ | data) ∝ -0.5*((θ-1.2)/0.3)^2 (Gaussian)
    def log_post(theta):
        return -0.5 * ((theta - 1.2) / 0.3) ** 2
    samples, accept = metropolis_hastings(log_post, x0=0.0,
                                          n_steps=3000, step_size=0.5)
    print(f"Acceptance rate: {accept*100:.0f}%")
    print(f"Posterior mean = {samples[500:].mean():.3f}  (truth 1.20)")
    print(f"Posterior std  = {samples[500:].std():.3f}   (truth 0.30)")

if __name__ == '__main__':
    demo()
