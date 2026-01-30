# Theory

Background theory and equations for phased array systems.

## Contents

| Topic | Description |
|-------|-------------|
| [Phased Array Fundamentals](phased-arrays.md) | Array factor, gain, beamwidth |
| [Link Budget Equations](link-budget-equations.md) | Communications link analysis |
| [Radar Equation](radar-equation.md) | Radar range and detection |
| [Pareto Optimization](pareto-optimization.md) | Multi-objective trade-offs |

## Quick Reference

### Antenna Gain

For a uniform rectangular array with \\(N = n_x \times n_y\\) elements:

\\[
G \approx \eta_a \cdot 4\pi \cdot n_x d_x \cdot n_y d_y
\\]

Where \\(\eta_a\\) is aperture efficiency (~0.6-0.7) and \\(d_x, d_y\\) are spacings in wavelengths.

### Free Space Path Loss

\\[
L_{FSPL} = 20 \log_{10}\left(\frac{4\pi d f}{c}\right) = 32.45 + 20\log_{10}(f_{MHz}) + 20\log_{10}(d_{km})
\\]

### Link Budget

\\[
\begin{aligned}
EIRP &= P_{tx} + G_{tx} - L_{tx} \\
P_{rx} &= EIRP - L_{path} + G_{rx} \\
SNR &= P_{rx} - N \\
Margin &= SNR - SNR_{required}
\end{aligned}
\\]

### Radar Range Equation

\\[
SNR = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k T_s B L}
\\]

### Pareto Optimality

Design \\(A\\) dominates design \\(B\\) if:

- \\(f_i(A) \leq f_i(B)\\) for all objectives (minimization)
- \\(f_j(A) < f_j(B)\\) for at least one objective

## Key Constants

| Constant | Symbol | Value |
|----------|--------|-------|
| Speed of light | \\(c\\) | 299,792,458 m/s |
| Boltzmann constant | \\(k\\) | 1.38×10⁻²³ J/K |
| Reference temperature | \\(T_0\\) | 290 K |

## Further Reading

- Skolnik, M.I., "Introduction to Radar Systems"
- Balanis, C.A., "Antenna Theory: Analysis and Design"
- Mailloux, R.J., "Phased Array Antenna Handbook"
