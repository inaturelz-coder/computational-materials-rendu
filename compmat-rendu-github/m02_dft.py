"""
m10_characterization.py — 督脉第 1 阶段：表征 — 数据源头

Demos:
  - XRD pattern from Bragg's law (Cu Kα, λ = 1.5406 Å) for simple cubic/fcc/bcc
  - Williamson-Hall peak broadening → grain size
  - Profile fit: pseudo-Voigt
"""

import numpy as np

LAMBDA_CU_KA = 1.5406  # Å, Cu Kα

# ---------- Bragg's law + structure factor selection ----------
def hkl_allowed(structure='fcc', hkl_max=4):
    """Generate allowed (hkl) for SC/BCC/FCC structures."""
    out = []
    for h in range(hkl_max + 1):
        for k in range(hkl_max + 1):
            for l in range(hkl_max + 1):
                if h == k == l == 0:
                    continue
                if structure == 'sc':
                    out.append((h, k, l))
                elif structure == 'bcc':
                    if (h + k + l) % 2 == 0:
                        out.append((h, k, l))
                elif structure == 'fcc':
                    if all(p % 2 == 0 for p in (h, k, l)) or \
                       all(p % 2 == 1 for p in (h, k, l)):
                        out.append((h, k, l))
    return out

def two_theta_from_hkl(a_lattice, hkl, wavelength=LAMBDA_CU_KA):
    """Bragg: λ = 2 d sin(θ), with d = a / sqrt(h²+k²+l²) for cubic."""
    h, k, l = hkl
    d = a_lattice / np.sqrt(h * h + k * k + l * l)
    sin_t = wavelength / (2 * d)
    if abs(sin_t) > 1:
        return None
    return 2 * np.degrees(np.arcsin(sin_t))

def xrd_pattern(a_lattice, structure='fcc', wavelength=LAMBDA_CU_KA, hkl_max=4):
    """Return sorted list of (hkl, 2θ_deg) for an ideal cubic powder pattern."""
    peaks = []
    seen_2theta = set()
    for hkl in hkl_allowed(structure, hkl_max):
        two_theta = two_theta_from_hkl(a_lattice, hkl, wavelength)
        if two_theta is None or two_theta > 140:
            continue
        # multiplicity-collapse: dedupe by 2θ
        key = round(two_theta, 4)
        if key in seen_2theta:
            continue
        seen_2theta.add(key)
        peaks.append((hkl, two_theta))
    return sorted(peaks, key=lambda x: x[1])

# ---------- Williamson-Hall ----------
def williamson_hall(two_theta_deg, fwhm_deg, wavelength=LAMBDA_CU_KA):
    """β cosθ = (Kλ/D) + 4ε sinθ.
    Linear fit of y = β cosθ vs x = sinθ gives:
       slope = 4ε (strain), intercept = Kλ/D → D = Kλ/intercept (Å)."""
    theta = np.radians(np.asarray(two_theta_deg) / 2)
    beta  = np.radians(np.asarray(fwhm_deg))
    y = beta * np.cos(theta)
    x = np.sin(theta)
    slope, intercept = np.polyfit(x, y, 1)
    K = 0.9
    D_A = K * wavelength / intercept                  # Å
    return {'crystallite_size_A': D_A, 'strain_eps': slope / 4.0}

# ---------- Pseudo-Voigt profile ----------
def pseudo_voigt(x, x0=0.0, fwhm=1.0, eta=0.5):
    """η Lorentzian + (1-η) Gaussian, both with same FWHM."""
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    gamma = fwhm / 2
    G = np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))
    L = gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)
    return eta * L + (1 - eta) * G

# ---------- Demo ----------
def demo():
    print("=== XRD pattern: Cu fcc (a = 3.615 Å, λ = Cu Kα) ===\n")
    pat = xrd_pattern(3.615, structure='fcc')
    print(f"  {'hkl':<10} {'2θ (deg)':>10}")
    for hkl, t in pat[:8]:
        print(f"  {str(hkl):<10} {t:>10.2f}")

    print("\n=== Williamson-Hall: extract crystallite size + strain ===\n")
    # Mock data
    two_theta = [43.3, 50.4, 74.1, 89.9]
    fwhm      = [0.18, 0.21, 0.27, 0.32]
    res = williamson_hall(two_theta, fwhm)
    print(f"  Crystallite size D ≈ {res['crystallite_size_A']:.0f} Å "
          f"({res['crystallite_size_A']/10:.0f} nm)")
    print(f"  Microstrain ε     ≈ {res['strain_eps']*100:.3f}%")

    print("\n=== Pseudo-Voigt at x=0 ===\n")
    x = np.linspace(-3, 3, 7)
    y = pseudo_voigt(x, fwhm=1.0, eta=0.5)
    for xi, yi in zip(x, y):
        print(f"  PV({xi:+.1f}) = {yi:.3f}")

if __name__ == '__main__':
    demo()
