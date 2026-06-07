"""
m05_phasefield.py — 任脉第 4 步：Phase-field (介观)

The classic: 1-D Cahn-Hilliard spinodal decomposition.
∂c/∂t = M ∇²(μ),  μ = ∂f/∂c - κ ∇²c,  f = W c²(1-c)²
Semi-implicit Fourier-space scheme (Eyre 1998).
"""

import numpy as np

def cahn_hilliard_1d(N=256, L=64.0, n_steps=8000, dt=0.05,
                     M=1.0, kappa=0.5, W=1.0, c0=0.5, noise=0.05, seed=0):
    """Simulate 1-D Cahn-Hilliard. Returns time series of c(x, t) at every 500 steps."""
    rng = np.random.default_rng(seed)
    dx = L / N
    c = c0 + noise * rng.standard_normal(N)

    # Fourier wavenumbers
    k = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    k2 = k * k
    k4 = k2 * k2

    snaps = [c.copy()]
    for step in range(n_steps):
        # Bulk derivative df/dc = 2 W c (1-c)(1-2c)
        dfdc = 2 * W * c * (1 - c) * (1 - 2 * c)
        # CH: ĉ_new = (ĉ - dt M k² f̂') / (1 + dt M kappa k⁴)   [Eyre semi-implicit]
        c_hat = np.fft.fft(c)
        f_hat = np.fft.fft(dfdc)
        c_hat = (c_hat - dt * M * k2 * f_hat) / (1.0 + dt * M * kappa * k4)
        c = np.real(np.fft.ifft(c_hat))
        if (step + 1) % 1000 == 0:
            snaps.append(c.copy())
    return np.array(snaps)

def domain_size(c, dx):
    """Estimate characteristic domain length from sign changes of (c-mean)."""
    s = np.sign(c - c.mean())
    crossings = np.sum(np.abs(np.diff(s)) > 0)
    return len(c) * dx / max(crossings, 1)

# ---------- Demo ----------
def demo():
    print("=== Cahn-Hilliard 1-D spinodal decomposition ===\n")
    snaps = cahn_hilliard_1d(N=256, L=64.0, n_steps=5000, dt=0.05,
                             M=1.0, kappa=0.5, W=1.0, c0=0.5, noise=0.05)
    dx = 64.0 / 256
    print(f"Snapshots collected: {len(snaps)} (every 1000 steps)")
    for i, c in enumerate(snaps):
        Lc = domain_size(c, dx)
        print(f"  step {i*1000:5d}: domain length ≈ {Lc:5.2f}  | "
              f"c-range [{c.min():.2f}, {c.max():.2f}]")
    print("\nNote how domain length grows ~ t^(1/3) (Lifshitz-Slyozov coarsening).")

if __name__ == '__main__':
    demo()
