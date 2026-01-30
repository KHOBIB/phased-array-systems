# Tutorial: Communications Trade Study

A complete walkthrough of designing a phased array for a communications link using DOE and Pareto analysis.

## Objective

By the end of this tutorial, you will:

- Define a communications scenario with requirements
- Create a design space for trade study
- Run a DOE batch evaluation
- Extract and rank Pareto-optimal designs
- Visualize trade-offs
- Export results

## Scenario

Design a phased array for a **100 km X-band communications link** with:

- Minimum 35 dBW EIRP
- Positive link margin
- Budget constraint of $100,000

## Step 1: Setup

```python
"""Communications array trade study tutorial."""

import matplotlib
matplotlib.use("Agg")  # For non-interactive environments
import matplotlib.pyplot as plt
from pathlib import Path

from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig, CostConfig
from phased_array_systems.scenarios import CommsLinkScenario
from phased_array_systems.requirements import Requirement, RequirementSet
from phased_array_systems.evaluate import evaluate_case
from phased_array_systems.trades import (
    DesignSpace,
    generate_doe,
    BatchRunner,
    filter_feasible,
    extract_pareto,
    rank_pareto,
)
from phased_array_systems.viz import pareto_plot, scatter_matrix
from phased_array_systems.io import export_results
```

## Step 2: Define the Scenario

```python
# Fixed operating conditions
scenario = CommsLinkScenario(
    freq_hz=10e9,              # 10 GHz (X-band)
    bandwidth_hz=10e6,         # 10 MHz bandwidth
    range_m=100e3,             # 100 km range
    required_snr_db=10.0,      # Required for demodulation
    scan_angle_deg=0.0,        # Boresight
    rx_antenna_gain_db=0.0,    # Isotropic receiver (worst case)
    rx_noise_temp_k=290.0,     # Room temperature
)

print(f"Scenario: {scenario.freq_hz/1e9:.1f} GHz, {scenario.range_m/1e3:.0f} km")
```

## Step 3: Define Requirements

```python
requirements = RequirementSet(
    requirements=[
        Requirement(
            id="REQ-001",
            name="Minimum EIRP",
            metric_key="eirp_dbw",
            op=">=",
            value=35.0,
            units="dBW",
            severity="must",
        ),
        Requirement(
            id="REQ-002",
            name="Positive Link Margin",
            metric_key="link_margin_db",
            op=">=",
            value=0.0,
            units="dB",
            severity="must",
        ),
        Requirement(
            id="REQ-003",
            name="Maximum Cost",
            metric_key="cost_usd",
            op="<=",
            value=100000.0,
            units="USD",
            severity="must",
        ),
    ],
    name="Comms Link Requirements",
)

print(f"Requirements: {len(requirements)} defined")
for req in requirements:
    print(f"  {req.id}: {req.name} ({req.metric_key} {req.op} {req.value})")
```

## Step 4: Define the Design Space

```python
design_space = (
    DesignSpace(name="Comms Array Trade Study")
    # Variable parameters (what we're exploring)
    .add_variable("array.nx", type="categorical", values=[4, 8, 16])
    .add_variable("array.ny", type="categorical", values=[4, 8, 16])
    .add_variable("rf.tx_power_w_per_elem", type="float", low=0.5, high=3.0)
    .add_variable("rf.pa_efficiency", type="float", low=0.2, high=0.5)
    .add_variable("cost.cost_per_elem_usd", type="float", low=75.0, high=150.0)
    # Fixed parameters (constants across all cases)
    .add_variable("array.geometry", type="categorical", values=["rectangular"])
    .add_variable("array.dx_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.dy_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.scan_limit_deg", type="float", low=60.0, high=60.0)
    .add_variable("array.enforce_subarray_constraint", type="categorical", values=[True])
    .add_variable("rf.noise_figure_db", type="float", low=3.0, high=3.0)
    .add_variable("rf.n_tx_beams", type="int", low=1, high=1)
    .add_variable("rf.feed_loss_db", type="float", low=1.0, high=1.0)
    .add_variable("rf.system_loss_db", type="float", low=0.0, high=0.0)
    .add_variable("cost.nre_usd", type="float", low=10000.0, high=10000.0)
    .add_variable("cost.integration_cost_usd", type="float", low=5000.0, high=5000.0)
)

print(f"\nDesign Space: {design_space.n_dims} dimensions")
print("Variable ranges:")
for var in design_space.variables:
    if var.type == "categorical" and len(var.values) > 1:
        print(f"  {var.name}: {var.values}")
    elif hasattr(var, 'low') and hasattr(var, 'high') and var.low != var.high:
        print(f"  {var.name}: [{var.low}, {var.high}]")
```

## Step 5: Generate DOE

```python
n_samples = 100
seed = 42

doe = generate_doe(
    design_space,
    method="lhs",  # Latin Hypercube Sampling
    n_samples=n_samples,
    seed=seed,
)

print(f"\nGenerated {len(doe)} cases using LHS (seed={seed})")
print(f"Columns: {list(doe.columns)[:5]}...")
```

## Step 6: Run Batch Evaluation

```python
runner = BatchRunner(scenario, requirements)

def progress_callback(completed, total):
    if completed % 20 == 0 or completed == total:
        pct = completed / total * 100
        print(f"  Progress: {completed}/{total} ({pct:.0f}%)")

print("\nRunning batch evaluation...")
results = runner.run(doe, n_workers=1, progress_callback=progress_callback)

# Check for errors
n_errors = results["meta.error"].notna().sum()
if n_errors > 0:
    print(f"Warning: {n_errors} cases had errors")

print(f"\nCompleted: {len(results)} cases")
```

## Step 7: Analyze Results

```python
# Create feasibility mask
feasible_mask = results["verification.passes"] == 1.0

# Filter to feasible
feasible = filter_feasible(results, requirements)

n_total = len(results)
n_feasible = len(feasible)
feasible_pct = n_feasible / n_total * 100

print(f"\nFeasibility Analysis:")
print(f"  Total cases: {n_total}")
print(f"  Feasible: {n_feasible} ({feasible_pct:.1f}%)")
print(f"  Infeasible: {n_total - n_feasible} ({100 - feasible_pct:.1f}%)")

# Metric ranges
print(f"\nMetric Ranges (all cases):")
print(f"  EIRP: {results['eirp_dbw'].min():.1f} to {results['eirp_dbw'].max():.1f} dBW")
print(f"  Cost: ${results['cost_usd'].min():,.0f} to ${results['cost_usd'].max():,.0f}")
print(f"  Margin: {results['link_margin_db'].min():.1f} to {results['link_margin_db'].max():.1f} dB")
```

## Step 8: Extract Pareto Frontier

```python
# Define objectives
objectives = [
    ("cost_usd", "minimize"),    # Lower cost is better
    ("eirp_dbw", "maximize"),    # Higher EIRP is better
]

# Extract Pareto-optimal designs
pareto = extract_pareto(feasible, objectives)
print(f"\nPareto-optimal designs: {len(pareto)}")

# Rank by weighted objectives
ranked = rank_pareto(pareto, objectives, weights=[0.5, 0.5])

print("\nTop 5 Pareto-optimal designs (balanced weights):")
print("-" * 70)
for i, (_, row) in enumerate(ranked.head(5).iterrows()):
    print(f"  #{i+1}: {row['case_id']}")
    print(f"      Array: {int(row['array.nx'])}×{int(row['array.ny'])} ({int(row['n_elements'])} elements)")
    print(f"      TX Power: {row['rf.tx_power_w_per_elem']:.2f} W/elem")
    print(f"      EIRP: {row['eirp_dbw']:.1f} dBW")
    print(f"      Cost: ${row['cost_usd']:,.0f}")
    print(f"      Margin: {row['link_margin_db']:.1f} dB")
```

## Step 9: Visualize Results

```python
# Create output directory
output_dir = Path("./tutorial_results")
output_dir.mkdir(exist_ok=True)

# Pareto plot: Cost vs EIRP
fig1 = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
    feasible_mask=feasible_mask,
    color_by="link_margin_db",
    title="Cost vs EIRP Trade Space",
    x_label="Total Cost (USD)",
    y_label="EIRP (dBW)",
    figsize=(10, 8),
)
fig1.savefig(output_dir / "pareto_cost_eirp.png", dpi=150, bbox_inches="tight")
print(f"Saved: {output_dir / 'pareto_cost_eirp.png'}")

# Scatter matrix of key metrics
fig2 = scatter_matrix(
    feasible,
    columns=["cost_usd", "eirp_dbw", "link_margin_db", "n_elements"],
    color_by="rf.tx_power_w_per_elem",
    diagonal="hist",
    title="Trade Space Correlations (Feasible Designs)",
    figsize=(12, 12),
)
fig2.savefig(output_dir / "scatter_matrix.png", dpi=150, bbox_inches="tight")
print(f"Saved: {output_dir / 'scatter_matrix.png'}")

plt.close("all")
```

## Step 10: Export Results

```python
# Export all results
export_results(results, output_dir / "all_results.parquet")
print(f"Saved: {output_dir / 'all_results.parquet'}")

# Export feasible results
export_results(feasible, output_dir / "feasible_results.parquet")
print(f"Saved: {output_dir / 'feasible_results.parquet'}")

# Export Pareto front to CSV for easy viewing
export_results(ranked, output_dir / "pareto_ranked.csv", format="csv")
print(f"Saved: {output_dir / 'pareto_ranked.csv'}")
```

## Step 11: Summary

```python
print("\n" + "=" * 70)
print("TRADE STUDY SUMMARY")
print("=" * 70)
print(f"Scenario: {scenario.freq_hz/1e9:.1f} GHz, {scenario.range_m/1e3:.0f} km")
print(f"Cases evaluated: {n_total}")
print(f"Feasible designs: {n_feasible} ({feasible_pct:.1f}%)")
print(f"Pareto-optimal: {len(pareto)}")

if len(ranked) > 0:
    best = ranked.iloc[0]
    print(f"\nBest Compromise Design: {best['case_id']}")
    print(f"  Array: {int(best['array.nx'])}×{int(best['array.ny'])}")
    print(f"  TX Power: {best['rf.tx_power_w_per_elem']:.2f} W/elem")
    print(f"  EIRP: {best['eirp_dbw']:.1f} dBW")
    print(f"  Link Margin: {best['link_margin_db']:.1f} dB")
    print(f"  Cost: ${best['cost_usd']:,.0f}")
    print(f"  Prime Power: {best['prime_power_w']:.0f} W")

print(f"\nResults saved to: {output_dir.absolute()}")
```

## Complete Code

The complete script is available at:
`examples/02_comms_doe_trade.py`

## Next Steps

- [Radar Detection Trade](radar-detection-trade.md) - Similar workflow for radar
- [Sensitivity Analysis](sensitivity-analysis.md) - Deep dive into parameter effects
- [User Guide: Pareto Analysis](../user-guide/pareto-analysis.md) - Advanced Pareto techniques
