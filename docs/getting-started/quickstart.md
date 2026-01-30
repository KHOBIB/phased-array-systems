# Quickstart

Get started with phased-array-systems in 5 minutes. This guide covers the essential workflow from defining an architecture to visualizing trade-offs.

## Single Case Evaluation

The simplest use case is evaluating a single array design.

### Step 1: Define the Architecture

```python
from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    RFChainConfig,
    CostConfig,
)

# Define the antenna array
array = ArrayConfig(
    geometry="rectangular",
    nx=8,                    # 8 elements in x
    ny=8,                    # 8 elements in y
    dx_lambda=0.5,           # Half-wavelength spacing
    dy_lambda=0.5,
    scan_limit_deg=60.0,     # Max scan angle
)

# Define the RF chain
rf = RFChainConfig(
    tx_power_w_per_elem=1.0,  # 1 Watt per element
    pa_efficiency=0.3,        # 30% PA efficiency
    noise_figure_db=3.0,      # 3 dB noise figure
)

# Define cost parameters
cost = CostConfig(
    cost_per_elem_usd=100.0,  # $100 per element
    nre_usd=10000.0,          # $10k NRE
)

# Combine into architecture
arch = Architecture(array=array, rf=rf, cost=cost, name="8x8 Baseline")
print(f"Array: {arch.array.nx}x{arch.array.ny} = {arch.n_elements} elements")
```

### Step 2: Define the Scenario

```python
from phased_array_systems.scenarios import CommsLinkScenario

scenario = CommsLinkScenario(
    freq_hz=10e9,           # 10 GHz (X-band)
    bandwidth_hz=10e6,      # 10 MHz bandwidth
    range_m=100e3,          # 100 km range
    required_snr_db=10.0,   # 10 dB required SNR
    scan_angle_deg=0.0,     # Boresight
    rx_antenna_gain_db=0.0, # Isotropic receiver
    rx_noise_temp_k=290.0,  # Room temperature
)
```

### Step 3: Evaluate

```python
from phased_array_systems.evaluate import evaluate_case

metrics = evaluate_case(arch, scenario)

# Print key results
print(f"EIRP: {metrics['eirp_dbw']:.1f} dBW")
print(f"Path Loss: {metrics['path_loss_db']:.1f} dB")
print(f"Received SNR: {metrics['snr_rx_db']:.1f} dB")
print(f"Link Margin: {metrics['link_margin_db']:.1f} dB")
print(f"Total Cost: ${metrics['cost_usd']:,.0f}")
```

Expected output:

```
EIRP: 45.1 dBW
Path Loss: 152.4 dB
Received SNR: 17.1 dB
Link Margin: 7.1 dB
Total Cost: $21,400
```

## Adding Requirements

Verify your design meets requirements:

```python
from phased_array_systems.requirements import Requirement, RequirementSet

requirements = RequirementSet(
    requirements=[
        Requirement(
            id="REQ-001",
            name="Minimum EIRP",
            metric_key="eirp_dbw",
            op=">=",
            value=40.0,
            severity="must",
        ),
        Requirement(
            id="REQ-002",
            name="Positive Link Margin",
            metric_key="link_margin_db",
            op=">=",
            value=0.0,
            severity="must",
        ),
        Requirement(
            id="REQ-003",
            name="Maximum Cost",
            metric_key="cost_usd",
            op="<=",
            value=50000.0,
            severity="must",
        ),
    ]
)

# Verify requirements
report = requirements.verify(metrics)
print(f"\nRequirements: {'PASS' if report.passes else 'FAIL'}")
print(f"  Must: {report.must_pass_count}/{report.must_total_count}")

for result in report.results:
    status = "PASS" if result.passes else "FAIL"
    print(f"  {result.requirement.id}: {status} (margin: {result.margin:.1f})")
```

## Trade Study Workflow

For more complex analysis, run a Design of Experiments (DOE):

### Step 1: Define the Design Space

```python
from phased_array_systems.trades import DesignSpace, generate_doe

# Define what parameters to vary
design_space = (
    DesignSpace(name="Array Trade Study")
    .add_variable("array.nx", type="categorical", values=[4, 8, 16])
    .add_variable("array.ny", type="categorical", values=[4, 8, 16])
    .add_variable("rf.tx_power_w_per_elem", type="float", low=0.5, high=3.0)
    .add_variable("cost.cost_per_elem_usd", type="float", low=75.0, high=150.0)
    # Fixed parameters
    .add_variable("array.geometry", type="categorical", values=["rectangular"])
    .add_variable("array.dx_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.dy_lambda", type="float", low=0.5, high=0.5)
    .add_variable("array.enforce_subarray_constraint", type="categorical", values=[True])
    .add_variable("rf.pa_efficiency", type="float", low=0.3, high=0.3)
    .add_variable("rf.noise_figure_db", type="float", low=3.0, high=3.0)
    .add_variable("cost.nre_usd", type="float", low=10000.0, high=10000.0)
)
```

### Step 2: Generate DOE and Evaluate

```python
from phased_array_systems.trades import BatchRunner

# Generate 50 samples using Latin Hypercube Sampling
doe = generate_doe(design_space, method="lhs", n_samples=50, seed=42)
print(f"Generated {len(doe)} cases")

# Run batch evaluation
runner = BatchRunner(scenario, requirements)
results = runner.run(doe, n_workers=1)

print(f"Completed: {len(results)} cases")
```

### Step 3: Extract Pareto Frontier

```python
from phased_array_systems.trades import extract_pareto, filter_feasible, rank_pareto

# Filter to feasible designs only
feasible = filter_feasible(results, requirements)
print(f"Feasible: {len(feasible)} / {len(results)}")

# Extract Pareto-optimal designs (minimize cost, maximize EIRP)
objectives = [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
]
pareto = extract_pareto(feasible, objectives)
print(f"Pareto-optimal: {len(pareto)} designs")

# Rank Pareto designs
ranked = rank_pareto(pareto, objectives, weights=[0.5, 0.5])

# Show top 3
print("\nTop 3 designs:")
for _, row in ranked.head(3).iterrows():
    print(f"  {row['case_id']}: ${row['cost_usd']:,.0f}, {row['eirp_dbw']:.1f} dBW")
```

### Step 4: Visualize

```python
from phased_array_systems.viz import pareto_plot
import matplotlib.pyplot as plt

# Create feasibility mask
feasible_mask = results["verification.passes"] == 1.0

# Generate Pareto plot
fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
    feasible_mask=feasible_mask,
    title="Cost vs EIRP Trade Space",
    x_label="Total Cost (USD)",
    y_label="EIRP (dBW)",
)
plt.savefig("pareto_plot.png", dpi=150, bbox_inches="tight")
plt.show()
```

## Using the CLI

The `pasys` command provides a quick way to run analyses:

```bash
# Run a single case from config file
pasys run config.yaml

# Run DOE with 100 samples
pasys doe config.yaml -n 100 --method lhs

# Generate report
pasys report results.parquet --format html

# Extract Pareto frontier
pasys pareto results.parquet -x cost_usd -y eirp_dbw --plot
```

## Complete Example

Here's the complete quickstart code in one block:

```python
"""Quickstart example for phased-array-systems."""

from phased_array_systems.architecture import (
    Architecture, ArrayConfig, RFChainConfig, CostConfig
)
from phased_array_systems.scenarios import CommsLinkScenario
from phased_array_systems.requirements import Requirement, RequirementSet
from phased_array_systems.evaluate import evaluate_case

# 1. Define architecture
arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
    cost=CostConfig(cost_per_elem_usd=100.0, nre_usd=10000.0),
)

# 2. Define scenario
scenario = CommsLinkScenario(
    freq_hz=10e9,
    bandwidth_hz=10e6,
    range_m=100e3,
    required_snr_db=10.0,
)

# 3. Define requirements
requirements = RequirementSet(requirements=[
    Requirement("REQ-001", "Min EIRP", "eirp_dbw", ">=", 40.0),
    Requirement("REQ-002", "Positive Margin", "link_margin_db", ">=", 0.0),
    Requirement("REQ-003", "Max Cost", "cost_usd", "<=", 50000.0),
])

# 4. Evaluate
metrics = evaluate_case(arch, scenario)

# 5. Verify requirements
report = requirements.verify(metrics)

# 6. Print results
print(f"EIRP: {metrics['eirp_dbw']:.1f} dBW")
print(f"Link Margin: {metrics['link_margin_db']:.1f} dB")
print(f"Cost: ${metrics['cost_usd']:,.0f}")
print(f"Requirements: {'PASS' if report.passes else 'FAIL'}")
```

## Next Steps

- [Learn core concepts](concepts.md) - Understand the architecture and design patterns
- [Architecture configuration](../user-guide/architecture.md) - Deep dive into configuration options
- [Trade studies](../user-guide/trade-studies.md) - Advanced DOE and optimization
- [Tutorials](../tutorials/index.md) - Step-by-step guides for common workflows
