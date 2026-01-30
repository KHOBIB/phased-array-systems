# pasys doe

Run a Design of Experiments (DOE) batch study.

## Synopsis

```bash
pasys doe <config> [options]
```

## Description

The `doe` command generates a design space sample and evaluates all cases. Results are saved as Parquet files for further analysis.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `config` | Yes | Path to configuration file (YAML or JSON) |

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `./results` | Output directory |
| `--samples` | `-n` | `50` | Number of DOE samples |
| `--method` | | `lhs` | Sampling method: `lhs`, `random`, `grid` |
| `--seed` | | `42` | Random seed |
| `--workers` | `-j` | `1` | Parallel workers |

## Sampling Methods

### Latin Hypercube Sampling (LHS)

Default and recommended. Space-filling design:

```bash
pasys doe config.yaml -n 100 --method lhs
```

### Random Sampling

Uniform random:

```bash
pasys doe config.yaml -n 100 --method random
```

### Grid Sampling

Full factorial (use with small design spaces):

```bash
pasys doe config.yaml --method grid
# Warning: Grid size grows exponentially!
```

## Parallel Execution

Use multiple workers for faster evaluation:

```bash
# 4 parallel workers
pasys doe config.yaml -n 200 -j 4
```

## Output

Results are saved to the output directory:

```
results/
└── results.parquet    # All case results
```

The Parquet file contains:

- Case ID and configuration parameters
- All computed metrics
- Requirement verification results
- Metadata (runtime, errors)

## Examples

### Basic DOE

```bash
pasys doe config.yaml -n 100
```

Output:

```
Design Space: 5 variables
Generating 100 samples using lhs...
Generated 100 cases using Latin Hypercube Sampling
Running batch evaluation...
  Progress: 10/100 (10%)
  Progress: 20/100 (20%)
  ...
  Progress: 100/100 (100%)

Completed: 100 cases
Feasible: 73 (73.0%)

Results saved to: ./results/results.parquet
```

### Full Study Pipeline

```bash
# Run DOE with custom settings
pasys doe study_config.yaml \
  -n 200 \
  --method lhs \
  --seed 12345 \
  -j 4 \
  -o ./study_results

# Extract Pareto
pasys pareto study_results/results.parquet -x cost_usd -y eirp_dbw

# Generate report
pasys report study_results/results.parquet -o report.html
```

### Reproducibility

Use the same seed for reproducible results:

```bash
# These produce identical results
pasys doe config.yaml -n 100 --seed 42
pasys doe config.yaml -n 100 --seed 42
```

## Configuration Requirements

The configuration file must include a `design_space` section:

```yaml
# config.yaml
name: "Trade Study"

architecture:
  # ... baseline configuration

scenario:
  # ... scenario definition

requirements:
  # ... requirements list

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

    # Fixed parameters (low == high)
    - name: array.geometry
      type: categorical
      values: [rectangular]

    - name: rf.pa_efficiency
      type: float
      low: 0.3
      high: 0.3
```

## Loading Results

```python
import pandas as pd

results = pd.read_parquet("results/results.parquet")

# Feasible designs
feasible = results[results["verification.passes"] == 1.0]

# Analyze
print(f"Total: {len(results)}")
print(f"Feasible: {len(feasible)}")
print(f"Cost range: ${results['cost_usd'].min():,.0f} - ${results['cost_usd'].max():,.0f}")
```

## Error Handling

```bash
# Missing design_space
pasys doe config_no_doe.yaml
# Error: Config must define a design_space for DOE

# Invalid variable specification
# Error messages indicate which variable has issues
```

## See Also

- [pasys run](run.md) - Single case evaluation
- [pasys pareto](pareto.md) - Pareto extraction
- [pasys report](report.md) - Report generation
- [User Guide: Trade Studies](../user-guide/trade-studies.md)
