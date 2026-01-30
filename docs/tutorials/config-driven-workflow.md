# Tutorial: Config-Driven Workflow

Use YAML configuration files for reproducible analysis.

## Objective

Learn to:

- Define studies in YAML configuration files
- Run analyses from the command line
- Maintain reproducible, version-controlled studies

## Why Config-Driven?

- **Reproducibility**: Track changes with git
- **Documentation**: Self-documenting study parameters
- **Automation**: Easy to script and batch
- **Collaboration**: Share configs with team

## Step 1: Create Configuration File

Create `study_config.yaml`:

```yaml
# study_config.yaml
# Communications array trade study configuration

name: "X-Band Comms Trade Study"

# System architecture (baseline values)
architecture:
  array:
    geometry: rectangular
    nx: 8
    ny: 8
    dx_lambda: 0.5
    dy_lambda: 0.5
    scan_limit_deg: 60.0
    max_subarray_nx: 8
    max_subarray_ny: 8
    enforce_subarray_constraint: true

  rf:
    tx_power_w_per_elem: 1.0
    pa_efficiency: 0.3
    noise_figure_db: 3.0
    n_tx_beams: 1
    feed_loss_db: 1.0
    system_loss_db: 0.0

  cost:
    cost_per_elem_usd: 100.0
    nre_usd: 10000.0
    integration_cost_usd: 5000.0

# Operating scenario
scenario:
  type: comms
  freq_hz: 10.0e9
  bandwidth_hz: 10.0e6
  range_m: 100.0e3
  required_snr_db: 10.0
  scan_angle_deg: 0.0
  rx_antenna_gain_db: 0.0
  rx_noise_temp_k: 290.0
  atmospheric_loss_db: 0.0
  rain_loss_db: 0.0

# Requirements
requirements:
  - id: REQ-001
    name: Minimum EIRP
    metric_key: eirp_dbw
    op: ">="
    value: 35.0
    units: dBW
    severity: must

  - id: REQ-002
    name: Positive Link Margin
    metric_key: link_margin_db
    op: ">="
    value: 0.0
    units: dB
    severity: must

  - id: REQ-003
    name: Maximum Cost
    metric_key: cost_usd
    op: "<="
    value: 100000.0
    units: USD
    severity: must

# Design space for DOE
design_space:
  variables:
    # Variable parameters
    - name: array.nx
      type: categorical
      values: [4, 8, 16]

    - name: array.ny
      type: categorical
      values: [4, 8, 16]

    - name: rf.tx_power_w_per_elem
      type: float
      low: 0.5
      high: 3.0

    - name: rf.pa_efficiency
      type: float
      low: 0.2
      high: 0.5

    - name: cost.cost_per_elem_usd
      type: float
      low: 75.0
      high: 150.0

    # Fixed parameters (low == high)
    - name: array.geometry
      type: categorical
      values: [rectangular]

    - name: array.dx_lambda
      type: float
      low: 0.5
      high: 0.5

    - name: array.dy_lambda
      type: float
      low: 0.5
      high: 0.5

    - name: array.enforce_subarray_constraint
      type: categorical
      values: [true]

    - name: rf.noise_figure_db
      type: float
      low: 3.0
      high: 3.0

    - name: rf.feed_loss_db
      type: float
      low: 1.0
      high: 1.0

    - name: cost.nre_usd
      type: float
      low: 10000.0
      high: 10000.0

    - name: cost.integration_cost_usd
      type: float
      low: 5000.0
      high: 5000.0
```

## Step 2: Single Case Evaluation (CLI)

Test the baseline configuration:

```bash
pasys run study_config.yaml
```

Output:

```
Results for study_config.yaml
============================================================

Antenna:
  g_peak_db: 24.0821
  ...

Link Budget:
  eirp_dbw: 45.0821
  link_margin_db: 7.0395
  ...

Cost:
  cost_usd: 21,400.0
```

## Step 3: Run DOE Study (CLI)

Execute the full trade study:

```bash
pasys doe study_config.yaml -n 100 --method lhs --seed 42 -o ./results
```

Output:

```
Design Space: 16 variables
Generating 100 samples using lhs...
Running batch evaluation...
  Progress: 10/100 (10%)
  ...
  Progress: 100/100 (100%)

Completed: 100 cases
Feasible: 73 (73.0%)

Results saved to: ./results/results.parquet
```

## Step 4: Extract Pareto (CLI)

```bash
pasys pareto results/results.parquet -x cost_usd -y eirp_dbw --plot
```

Output:

```
Pareto Frontier: 12 designs
======================================================================
  case_00023: cost_usd=18234.50, eirp_dbw=38.21
  case_00045: cost_usd=23567.00, eirp_dbw=42.15
  ...

Plot saved to: pareto_plot.png
```

## Step 5: Generate Report (CLI)

```bash
pasys report results/results.parquet --title "X-Band Trade Study" -o report.html
```

## Step 6: Python Integration

Use configs in Python scripts:

```python
from phased_array_systems.io import load_config
from phased_array_systems.evaluate import evaluate_case
from phased_array_systems.trades import generate_doe, BatchRunner

# Load configuration
config = load_config("study_config.yaml")

# Extract components
arch = config.get_architecture()
scenario = config.get_scenario()
requirements = config.get_requirement_set()

# Single case
metrics = evaluate_case(arch, scenario)
report = requirements.verify(metrics)
print(f"Baseline passes: {report.passes}")

# DOE study
design_space = config.get_design_space()  # If implemented
```

## Step 7: Version Control

Track your study with git:

```bash
# Initialize repo
git init
git add study_config.yaml
git commit -m "Initial trade study configuration"

# After running study
git add results/
git commit -m "Trade study results: 100 cases, 73 feasible"

# Modify and re-run
# Edit study_config.yaml
git add study_config.yaml
git commit -m "Increase power range to 0.5-4.0 W"
```

## Step 8: Sensitivity Studies

Create variants for sensitivity analysis:

```yaml
# study_config_high_power.yaml
# Copy and modify
name: "High Power Variant"

architecture:
  rf:
    tx_power_w_per_elem: 2.0  # Changed from 1.0

# ... rest same
```

Run both:

```bash
pasys doe study_config.yaml -n 100 -o ./results_baseline
pasys doe study_config_high_power.yaml -n 100 -o ./results_high_power
```

## Step 9: Automation Script

Create a shell script for the complete workflow:

```bash
#!/bin/bash
# run_study.sh

CONFIG=$1
OUTPUT_DIR=$2
N_SAMPLES=${3:-100}

echo "Running study: $CONFIG"
echo "Output: $OUTPUT_DIR"
echo "Samples: $N_SAMPLES"

# Run DOE
pasys doe $CONFIG -n $N_SAMPLES --seed 42 -o $OUTPUT_DIR

# Extract Pareto
pasys pareto $OUTPUT_DIR/results.parquet -x cost_usd -y eirp_dbw \
    --plot -o $OUTPUT_DIR/pareto.csv

# Generate report
pasys report $OUTPUT_DIR/results.parquet \
    --title "Trade Study Report" \
    -o $OUTPUT_DIR/report.html

echo "Study complete: $OUTPUT_DIR"
```

Usage:

```bash
chmod +x run_study.sh
./run_study.sh study_config.yaml ./results 100
```

## Best Practices

### 1. Use Descriptive Names

```yaml
name: "Q4-2024 Array Redesign - 150km Range"
```

### 2. Comment Important Values

```yaml
scenario:
  freq_hz: 10.0e9       # X-band
  range_m: 150.0e3      # Increased from 100 km (customer request)
  required_snr_db: 12.0  # 16-QAM modulation
```

### 3. Organize Configs by Study

```
studies/
├── baseline/
│   ├── config.yaml
│   └── results/
├── high_power/
│   ├── config.yaml
│   └── results/
└── extended_range/
    ├── config.yaml
    └── results/
```

### 4. Include Metadata

```yaml
# metadata (optional, for documentation)
metadata:
  author: "Engineering Team"
  date: "2024-01-15"
  version: "1.2"
  description: |
    Trade study for next-generation comms array.
    Explores 4x4 to 16x16 configurations.
```

## Next Steps

- [Communications Trade Study](comms-trade-study.md) - Full Python workflow
- [Sensitivity Analysis](sensitivity-analysis.md) - Parameter studies
- [CLI Reference](../cli/index.md) - Command details
