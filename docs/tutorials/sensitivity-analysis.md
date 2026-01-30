# Tutorial: Sensitivity Analysis

Understand how design parameters affect performance.

## Objective

Learn to:

- Identify sensitive parameters
- Visualize parameter effects
- Use scatter matrices for correlation analysis
- Perform one-at-a-time (OAT) sensitivity studies

## Overview

Sensitivity analysis answers: "Which parameters matter most?"

This helps:
- Focus design effort on critical parameters
- Identify parameters that can be relaxed
- Understand design robustness

## Step 1: Setup

```python
"""Sensitivity analysis tutorial."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig, CostConfig
from phased_array_systems.scenarios import CommsLinkScenario
from phased_array_systems.evaluate import evaluate_case
from phased_array_systems.trades import DesignSpace, generate_doe, BatchRunner
from phased_array_systems.viz import scatter_matrix
```

## Step 2: Define Baseline

```python
# Baseline configuration
baseline_arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
    cost=CostConfig(cost_per_elem_usd=100.0, nre_usd=10000.0),
)

scenario = CommsLinkScenario(
    freq_hz=10e9,
    bandwidth_hz=10e6,
    range_m=100e3,
    required_snr_db=10.0,
)

# Baseline metrics
baseline_metrics = evaluate_case(baseline_arch, scenario)
print(f"Baseline: 8×8 array, 1.0 W/elem")
print(f"  EIRP: {baseline_metrics['eirp_dbw']:.1f} dBW")
print(f"  Link Margin: {baseline_metrics['link_margin_db']:.1f} dB")
print(f"  Cost: ${baseline_metrics['cost_usd']:,.0f}")
```

## Step 3: One-at-a-Time (OAT) Sensitivity

Vary one parameter while holding others constant:

```python
def oat_sensitivity(param_name, values, baseline_flat, scenario):
    """Perform one-at-a-time sensitivity analysis."""
    results = []

    for value in values:
        # Copy baseline and modify one parameter
        params = baseline_flat.copy()
        params[param_name] = value

        # Create architecture
        arch = Architecture.from_flat(params)

        # Evaluate
        metrics = evaluate_case(arch, scenario)
        metrics[param_name] = value
        results.append(metrics)

    return pd.DataFrame(results)

# Get baseline as flat dict
baseline_flat = baseline_arch.model_dump_flat()

# Define parameter ranges to sweep
param_sweeps = {
    "array.nx": [4, 8, 12, 16],  # Note: some may violate sub-array constraint
    "rf.tx_power_w_per_elem": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
    "rf.pa_efficiency": [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
    "cost.cost_per_elem_usd": [50, 75, 100, 125, 150, 175, 200],
}
```

## Step 4: Run OAT Analysis

```python
# Disable sub-array constraint for continuous sweep
baseline_flat["array.enforce_subarray_constraint"] = False

# Sweep TX power (key driver of EIRP)
print("\n=== TX Power Sensitivity ===")
tx_power_results = oat_sensitivity(
    "rf.tx_power_w_per_elem",
    [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
    baseline_flat,
    scenario,
)

print(f"TX Power (W) | EIRP (dBW) | Margin (dB) | Cost ($)")
print("-" * 55)
for _, row in tx_power_results.iterrows():
    print(f"{row['rf.tx_power_w_per_elem']:12.1f} | "
          f"{row['eirp_dbw']:10.1f} | "
          f"{row['link_margin_db']:10.1f} | "
          f"{row['cost_usd']:,.0f}")

# Sweep PA efficiency (affects power consumption)
print("\n=== PA Efficiency Sensitivity ===")
pa_eff_results = oat_sensitivity(
    "rf.pa_efficiency",
    [0.2, 0.25, 0.3, 0.35, 0.4, 0.5],
    baseline_flat,
    scenario,
)

print(f"Efficiency | Prime Power (W) | DC Power (W)")
print("-" * 45)
for _, row in pa_eff_results.iterrows():
    print(f"{row['rf.pa_efficiency']:10.2f} | "
          f"{row['prime_power_w']:15.0f} | "
          f"{row['dc_power_w']:.0f}")
```

## Step 5: Visualize OAT Results

```python
output_dir = Path("./sensitivity_results")
output_dir.mkdir(exist_ok=True)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# TX Power vs EIRP
ax = axes[0, 0]
ax.plot(tx_power_results["rf.tx_power_w_per_elem"],
        tx_power_results["eirp_dbw"], 'bo-')
ax.set_xlabel("TX Power per Element (W)")
ax.set_ylabel("EIRP (dBW)")
ax.set_title("TX Power → EIRP")
ax.grid(True, alpha=0.3)

# TX Power vs Link Margin
ax = axes[0, 1]
ax.plot(tx_power_results["rf.tx_power_w_per_elem"],
        tx_power_results["link_margin_db"], 'go-')
ax.axhline(y=0, color='r', linestyle='--', label='Min Margin')
ax.set_xlabel("TX Power per Element (W)")
ax.set_ylabel("Link Margin (dB)")
ax.set_title("TX Power → Link Margin")
ax.grid(True, alpha=0.3)
ax.legend()

# PA Efficiency vs Prime Power
ax = axes[1, 0]
ax.plot(pa_eff_results["rf.pa_efficiency"],
        pa_eff_results["prime_power_w"], 'mo-')
ax.set_xlabel("PA Efficiency")
ax.set_ylabel("Prime Power (W)")
ax.set_title("PA Efficiency → Prime Power")
ax.grid(True, alpha=0.3)

# Cost per Element vs Total Cost
cost_results = oat_sensitivity(
    "cost.cost_per_elem_usd",
    [50, 75, 100, 125, 150, 200],
    baseline_flat,
    scenario,
)
ax = axes[1, 1]
ax.plot(cost_results["cost.cost_per_elem_usd"],
        cost_results["cost_usd"], 'ro-')
ax.set_xlabel("Cost per Element (USD)")
ax.set_ylabel("Total Cost (USD)")
ax.set_title("Element Cost → Total Cost")
ax.grid(True, alpha=0.3)

fig.suptitle("One-at-a-Time Sensitivity Analysis", fontsize=14)
fig.tight_layout()
fig.savefig(output_dir / "oat_sensitivity.png", dpi=150)
plt.close()

print(f"\nSaved: {output_dir / 'oat_sensitivity.png'}")
```

## Step 6: Global Sensitivity via DOE

OAT misses interactions. Use DOE for global sensitivity:

```python
# Full DOE for global sensitivity
space = (
    DesignSpace(name="Sensitivity Study")
    .add_variable("array.nx", type="categorical", values=[4, 8, 16])
    .add_variable("array.ny", type="categorical", values=[4, 8, 16])
    .add_variable("rf.tx_power_w_per_elem", type="float", low=0.5, high=3.0)
    .add_variable("rf.pa_efficiency", type="float", low=0.2, high=0.5)
    .add_variable("cost.cost_per_elem_usd", type="float", low=50.0, high=200.0)
    # Fixed
    .add_variable("array.geometry", type="categorical", values=["rectangular"])
    .add_variable("array.dx_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.dy_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.enforce_subarray_constraint", type="categorical", values=[True])
    .add_variable("rf.noise_figure_db", type="float", low=3.0, high=3.0)
    .add_variable("cost.nre_usd", type="float", low=10000.0, high=10000.0)
)

doe = generate_doe(space, method="lhs", n_samples=200, seed=42)
runner = BatchRunner(scenario)
results = runner.run(doe, n_workers=1)

print(f"Evaluated {len(results)} cases for global sensitivity")
```

## Step 7: Correlation Analysis

```python
# Compute correlations
input_cols = ["array.nx", "array.ny", "rf.tx_power_w_per_elem",
              "rf.pa_efficiency", "cost.cost_per_elem_usd"]
output_cols = ["eirp_dbw", "link_margin_db", "cost_usd", "prime_power_w"]

# Input-output correlations
print("\n=== Input-Output Correlations ===")
print(f"{'Input':<30} | {'EIRP':>8} | {'Margin':>8} | {'Cost':>8} | {'Power':>8}")
print("-" * 80)

for inp in input_cols:
    corrs = []
    for out in output_cols:
        corr = results[inp].corr(results[out])
        corrs.append(corr)
    print(f"{inp:<30} | {corrs[0]:>8.3f} | {corrs[1]:>8.3f} | {corrs[2]:>8.3f} | {corrs[3]:>8.3f}")
```

## Step 8: Scatter Matrix Visualization

```python
# Scatter matrix showing relationships
fig = scatter_matrix(
    results,
    columns=["array.nx", "rf.tx_power_w_per_elem", "eirp_dbw",
             "link_margin_db", "cost_usd"],
    color_by="prime_power_w",
    diagonal="hist",
    title="Design Space Correlations",
    figsize=(14, 14),
)
fig.savefig(output_dir / "scatter_matrix.png", dpi=150)
plt.close()
print(f"Saved: {output_dir / 'scatter_matrix.png'}")
```

## Step 9: Identify Key Drivers

```python
# Rank parameters by correlation magnitude
print("\n=== Parameter Importance (by |correlation| with EIRP) ===")
importance = []
for inp in input_cols:
    corr = abs(results[inp].corr(results["eirp_dbw"]))
    importance.append((inp, corr))

importance.sort(key=lambda x: x[1], reverse=True)
for param, corr in importance:
    print(f"  {param}: {corr:.3f}")
```

## Step 10: Robustness Analysis

Evaluate performance variation around the baseline:

```python
# Add noise to baseline and evaluate
np.random.seed(42)
n_monte_carlo = 100

# Define parameter uncertainties (±%)
uncertainties = {
    "rf.tx_power_w_per_elem": 0.10,  # ±10%
    "rf.pa_efficiency": 0.05,         # ±5%
    "cost.cost_per_elem_usd": 0.15,   # ±15%
}

mc_results = []
for _ in range(n_monte_carlo):
    params = baseline_flat.copy()

    # Apply random perturbations
    for param, pct in uncertainties.items():
        nominal = baseline_flat[param]
        perturbed = nominal * (1 + np.random.uniform(-pct, pct))
        params[param] = perturbed

    arch = Architecture.from_flat(params)
    metrics = evaluate_case(arch, scenario)
    mc_results.append(metrics)

mc_df = pd.DataFrame(mc_results)

print("\n=== Robustness Analysis (Monte Carlo) ===")
print(f"Based on {n_monte_carlo} samples with parameter uncertainties")
print(f"\nEIRP (dBW):")
print(f"  Mean: {mc_df['eirp_dbw'].mean():.2f}")
print(f"  Std:  {mc_df['eirp_dbw'].std():.2f}")
print(f"  Range: [{mc_df['eirp_dbw'].min():.2f}, {mc_df['eirp_dbw'].max():.2f}]")

print(f"\nLink Margin (dB):")
print(f"  Mean: {mc_df['link_margin_db'].mean():.2f}")
print(f"  Std:  {mc_df['link_margin_db'].std():.2f}")
print(f"  Min margin: {mc_df['link_margin_db'].min():.2f}")
```

## Key Insights

### High-Impact Parameters

From typical analyses:

1. **Array Size (nx, ny)**: Strongest driver of EIRP and cost
2. **TX Power**: Linear effect on EIRP, major power driver
3. **Element Cost**: Direct cost driver
4. **PA Efficiency**: Power consumption driver

### Low-Impact Parameters

Parameters that can often be relaxed:

1. **Exact spacing**: 0.45-0.55λ typically similar performance
2. **Noise figure**: Usually second-order effect on SNR

### Interactions

- Array size × TX power: Can trade off (larger array, lower power)
- PA efficiency × TX power: Both affect DC power

## Best Practices

1. **Start with OAT**: Quick understanding of individual effects
2. **Use DOE for interactions**: Captures multi-parameter effects
3. **Focus on sensitivities**: Concentrate design effort on sensitive parameters
4. **Validate with Monte Carlo**: Understand robustness to uncertainties

## Next Steps

- [Communications Trade Study](comms-trade-study.md) - Apply to full study
- [Pareto Analysis](../user-guide/pareto-analysis.md) - Multi-objective trade-offs
- [Theory: Link Budget](../theory/link-budget-equations.md) - Understand equations
