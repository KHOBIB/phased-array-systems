# pasys pareto

Extract and display the Pareto frontier.

## Synopsis

```bash
pasys pareto <results> -x <metric> -y <metric> [options]
```

## Description

The `pareto` command extracts Pareto-optimal designs from results, displays the top designs, and optionally generates a plot.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `results` | Yes | Path to results file (Parquet or CSV) |

## Options

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `-x` | | Yes | | X-axis metric (minimized) |
| `-y` | | Yes | | Y-axis metric (maximized) |
| `--output` | `-o` | No | None | Save Pareto front to file |
| `--plot` | | No | False | Generate plot |

## Objective Directions

By default:
- **X-axis**: Minimized (e.g., cost)
- **Y-axis**: Maximized (e.g., performance)

This covers the common "minimize cost, maximize performance" trade-off.

## Examples

### Basic Extraction

```bash
pasys pareto results.parquet -x cost_usd -y eirp_dbw
```

Output:

```
Pareto Frontier: 12 designs
======================================================================
  case_00023: cost_usd=18234.50, eirp_dbw=38.21
  case_00045: cost_usd=23567.00, eirp_dbw=42.15
  case_00067: cost_usd=31245.00, eirp_dbw=45.67
  case_00012: cost_usd=42890.00, eirp_dbw=48.23
  case_00089: cost_usd=56123.00, eirp_dbw=51.45
  ...
```

### Save to File

```bash
pasys pareto results.parquet -x cost_usd -y eirp_dbw -o pareto.csv
```

Creates `pareto.csv` with all Pareto-optimal designs.

### Generate Plot

```bash
pasys pareto results.parquet -x cost_usd -y eirp_dbw --plot
```

Creates `pareto_plot.png` showing:
- All designs as blue points
- Pareto-optimal designs as red points
- Pareto frontier line

### Save Plot with Custom Name

```bash
pasys pareto results.parquet -x cost_usd -y eirp_dbw -o pareto.csv --plot
# Creates: pareto.csv and pareto.png
```

## Common Metric Combinations

### Cost vs. Performance

```bash
# Cost vs. EIRP (communications)
pasys pareto results.parquet -x cost_usd -y eirp_dbw

# Cost vs. SNR margin
pasys pareto results.parquet -x cost_usd -y link_margin_db

# Cost vs. detection range (radar)
pasys pareto results.parquet -x cost_usd -y snr_margin_db
```

### Power vs. Performance

```bash
# Power vs. EIRP
pasys pareto results.parquet -x prime_power_w -y eirp_dbw
```

### Size vs. Performance

```bash
# Element count vs. EIRP
pasys pareto results.parquet -x n_elements -y eirp_dbw
```

## Output Format

### Display

Shows top 10 Pareto designs with:
- Case ID
- X metric value
- Y metric value

### CSV Export

Full DataFrame with all columns for Pareto-optimal designs:
- All input parameters
- All computed metrics
- Verification results
- Pareto rank and score

### Plot

PNG image with:
- All designs (blue circles)
- Pareto-optimal designs (red circles)
- Connecting line through Pareto front
- Axis labels
- Grid

## Workflow Example

```bash
# 1. Run DOE
pasys doe config.yaml -n 200 -o ./study

# 2. Extract Pareto frontier
pasys pareto study/results.parquet -x cost_usd -y eirp_dbw --plot -o study/pareto.csv

# 3. View results
cat study/pareto.csv | head -20
open study/pareto.png  # macOS

# 4. Alternative trade-offs
pasys pareto study/results.parquet -x prime_power_w -y eirp_dbw --plot
```

## Filtering

The Pareto extraction uses the `verification.passes` column to filter feasible designs before extracting the frontier. Only designs that pass all "must" requirements are considered.

## Error Handling

```bash
# File not found
pasys pareto missing.parquet -x cost_usd -y eirp_dbw
# Error: Results file not found: missing.parquet

# Column not found
pasys pareto results.parquet -x invalid_metric -y eirp_dbw
# Error: Column 'invalid_metric' not found in results
```

## See Also

- [pasys doe](doe.md) - Generate results
- [pasys report](report.md) - Full reports
- [User Guide: Pareto Analysis](../user-guide/pareto-analysis.md)
- [Trades API](../api/trades.md) - Programmatic Pareto analysis
