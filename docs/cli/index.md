# CLI Reference

The `pasys` command-line interface provides quick access to common operations.

## Installation

The CLI is installed automatically with the package:

```bash
pip install phased-array-systems
```

Verify installation:

```bash
pasys --version
```

## Commands

| Command | Description |
|---------|-------------|
| [`pasys run`](run.md) | Single-case evaluation |
| [`pasys doe`](doe.md) | DOE batch study |
| [`pasys report`](report.md) | Generate report |
| [`pasys pareto`](pareto.md) | Extract Pareto frontier |

## Quick Reference

```bash
# Single case evaluation
pasys run config.yaml
pasys run config.yaml --format json
pasys run config.yaml -o results.json

# DOE batch study
pasys doe config.yaml -n 100
pasys doe config.yaml -n 100 --method lhs --seed 42
pasys doe config.yaml -n 100 -j 4  # 4 parallel workers

# Generate report
pasys report results.parquet
pasys report results.parquet --format html -o report.html
pasys report results.parquet --format markdown --title "Q4 Study"

# Extract Pareto frontier
pasys pareto results.parquet -x cost_usd -y eirp_dbw
pasys pareto results.parquet -x cost_usd -y eirp_dbw --plot
pasys pareto results.parquet -x cost_usd -y eirp_dbw -o pareto.csv
```

## Global Options

```bash
pasys --version      # Show version
pasys --help         # Show help
pasys <command> -h   # Command-specific help
```

## Configuration File Format

All commands accept YAML or JSON configuration files:

```yaml
# config.yaml
name: "My Trade Study"

architecture:
  array:
    geometry: rectangular
    nx: 8
    ny: 8
    dx_lambda: 0.5
    dy_lambda: 0.5
  rf:
    tx_power_w_per_elem: 1.0
    pa_efficiency: 0.3
  cost:
    cost_per_elem_usd: 100.0

scenario:
  type: comms
  freq_hz: 10.0e9
  bandwidth_hz: 10.0e6
  range_m: 100.0e3
  required_snr_db: 10.0

requirements:
  - id: REQ-001
    name: Minimum EIRP
    metric_key: eirp_dbw
    op: ">="
    value: 40.0
    severity: must

# For DOE (pasys doe only)
design_space:
  variables:
    - name: array.nx
      type: categorical
      values: [4, 8, 16]
    - name: rf.tx_power_w_per_elem
      type: float
      low: 0.5
      high: 3.0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, invalid config, etc.) |

## Examples

### Complete Workflow

```bash
# 1. Run DOE study
pasys doe config.yaml -n 100 --seed 42 -o ./results

# 2. Extract Pareto and plot
pasys pareto results/results.parquet -x cost_usd -y eirp_dbw --plot

# 3. Generate report
pasys report results/results.parquet --title "Trade Study" -o report.html
```

### Quick Evaluation

```bash
# Evaluate single configuration
pasys run config.yaml --format table

# Output as JSON for scripting
pasys run config.yaml --format json | jq '.link_margin_db'
```

## See Also

- [User Guide: Trade Studies](../user-guide/trade-studies.md)
- [I/O API](../api/io.md) - Configuration schema
