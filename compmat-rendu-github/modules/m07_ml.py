"""
m07_ml.py — 督脉第 2 阶段：ML for Materials

Demos:
  - Gaussian Process regression with RBF kernel (from scratch, no sklearn)
  - Predict + uncertainty on a 1-D toy "materials property" landscape
  - LOO-CV error
"""

import numpy as np

# ---------- RBF kernel ----------
def rbf(X1, X2, length=1.0, sigma_f=1.0):
    """k(x, x') = σ² exp(- ||x-x'||² / 2l²)."""
    diff = X1[:, None, :] - X2[None, :, :]
    sq = (diff ** 2).sum(axis=-1)
    return (sigma_f ** 2) * np.exp(-0.5 * sq / (length ** 2))

# ---------- GP regression ----------
class GP:
    def __init__(self, length=1.0, sigma_f=1.0, sigma_n=1e-3):
        self.length = length
        self.sigma_f = sigma_f
        self.sigma_n = sigma_n

    def fit(self, X, y):
        self.X = np.atleast_2d(X)
        self.y = np.asarray(y).reshape(-1)
        K = rbf(self.X, self.X, self.length, self.sigma_f)
        K += (self.sigma_n ** 2) * np.eye(len(self.X))
        self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T,
                                     np.linalg.solve(self.L, self.y))
        return self

    def predict(self, X_star, return_std=True):
        Xs = np.atleast_2d(X_star)
        K_s = rbf(self.X, Xs, self.length, self.sigma_f)
        mu = K_s.T @ self.alpha
        if not return_std:
            return mu
        v = np.linalg.solve(self.L, K_s)
        K_ss = rbf(Xs, Xs, self.length, self.sigma_f)
        var = np.diag(K_ss) - np.sum(v ** 2, axis=0)
        std = np.sqrt(np.clip(var, 1e-12, None))
        return mu, std

    def loo_rmse(self):
        """Leave-One-Out RMSE via Rasmussen 5.12 (no refit)."""
        K = rbf(self.X, self.X, self.length, self.sigma_f) + \
            (self.sigma_n ** 2) * np.eye(len(self.X))
        K_inv = np.linalg.inv(K)
        residuals = self.alpha / np.diag(K_inv)
        return float(np.sqrt((residuals ** 2).mean()))

# ---------- Demo ----------
def demo():
    print("=== GP regression on toy materials property ===\n")
    rng = np.random.default_rng(0)
    # Hidden "materials property" function (e.g. yield strength vs composition)
    def f_true(x):
        return np.sin(2.5 * x) + 0.5 * x

    # Training points (sparse, noisy)
    X_train = rng.uniform(0, 3, size=(8, 1))
    y_train = f_true(X_train.ravel()) + 0.05 * rng.standard_normal(8)

    # Fit
    gp = GP(length=0.7, sigma_f=1.0, sigma_n=0.05).fit(X_train, y_train)
    print(f"LOO-CV RMSE = {gp.loo_rmse():.3f}")

    # Predict on dense grid
    X_star = np.linspace(0, 3, 30).reshape(-1, 1)
    mu, std = gp.predict(X_star)

    print("\n  x      μ_pred   2σ     truth")
    for i in range(0, 30, 5):
        x = float(X_star[i])
        print(f" {x:.2f}    {mu[i]:+.3f}   ±{2*std[i]:.3f}   {f_true(x):+.3f}")

    print("\n→ GP gives prediction + uncertainty in a single forward pass.")
    print("  Use std as the 'don't trust me here' indicator for active learning.")

if __name__ == '__main__':
    demo()
