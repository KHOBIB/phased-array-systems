# Frequently Asked Questions

Common questions about phased-array-systems.

## Installation

### Q: How do I install phased-array-systems?

```bash
pip install phased-array-systems
```

For all features:

```bash
pip install phased-array-systems[dev,plotting,docs]
```

### Q: What Python versions are supported?

Python 3.10 and later.

### Q: I get an error about phased-array-modeling not found

Install it explicitly:

```bash
pip install phased-array-modeling>=1.2.0
```

## Configuration

### Q: Why do array dimensions need to be powers of 2?

This is the sub-array constraint for practical RF component design. Arrays are typically built from sub-arrays (e.g., 8×8 tiles), and dimensions must be compatible with this tiling.

To disable:

```python
ArrayConfig(nx=10, ny=10, enforce_subarray_constraint=False)
```

### Q: What's the difference between `must`, `should`, and `nice` requirements?

| Severity | Meaning | Effect |
|----------|---------|--------|
| `must` | Mandatory | Fails verification if not met |
| `should` | Desired | Tracked but doesn't fail |
| `nice` | Optional | Tracked but doesn't fail |

### Q: How do I fix "metric not found" errors in requirements?

Ensure the `metric_key` matches exactly the key returned by `evaluate_case()`. Common keys:

- `eirp_dbw` (not `eirp` or `EIRP`)
- `link_margin_db` (not `margin`)
- `cost_usd` (not `cost`)

## Trade Studies

### Q: How many DOE samples should I use?

| Design Space Size | Recommended Samples |
|-------------------|---------------------|
| < 5 variables | 50-100 |
| 5-10 variables | 100-200 |
| > 10 variables | 200+ |

Use Latin Hypercube Sampling (LHS) for best coverage.

### Q: Why are all my designs infeasible?

Common causes:

1. **Requirements too strict**: Relax thresholds
2. **Design space too narrow**: Expand bounds
3. **Conflicting requirements**: Check if requirements are achievable together

Debug:

```python
# Check what's failing
report = requirements.verify(metrics)
for result in report.results:
    print(f"{result.requirement.id}: {result.passes}, margin={result.margin}")
```

### Q: Can I run evaluations in parallel?

Yes, use `n_workers`:

```python
runner = BatchRunner(scenario, requirements)
results = runner.run(doe, n_workers=4)
```

### Q: How do I add more samples to an existing study?

```python
from phased_array_systems.trades import augment_doe

expanded = augment_doe(existing_doe, design_space, n_additional=50, seed=43)
new_cases = expanded[~expanded["case_id"].isin(existing_doe["case_id"])]
new_results = runner.run(new_cases)
```

## Pareto Analysis

### Q: What does "Pareto optimal" mean?

A design is Pareto optimal if no other design is better in ALL objectives. Improving one objective requires sacrificing another.

### Q: How do I choose weights for ranking?

Weights reflect stakeholder priorities:

- Cost-conscious: `weights=[0.8, 0.2]`
- Balanced: `weights=[0.5, 0.5]`
- Performance-focused: `weights=[0.2, 0.8]`

Present rankings under multiple scenarios.

### Q: Why is my Pareto front empty?

Check that you're using feasible designs:

```python
feasible = filter_feasible(results, requirements)
pareto = extract_pareto(feasible, objectives)  # Not results!
```

## Performance

### Q: Evaluation is slow. How can I speed it up?

1. Use parallel workers: `n_workers=4`
2. Reduce DOE size for initial exploration
3. Simplify antenna model if full pattern not needed

### Q: Memory usage is high with large DOE

Results are stored as pandas DataFrame. For very large studies:

```python
# Export incrementally
for batch in batches:
    results = runner.run(batch)
    export_results(results, f"batch_{i}.parquet")
```

## Models

### Q: How is antenna gain calculated?

If pre-computed antenna metrics aren't provided, gain is approximated:

\\[G \approx \eta \cdot 4\pi \cdot n_x d_x \cdot n_y d_y\\]

For accurate patterns, use the full antenna adapter with `phased-array-modeling`.

### Q: What propagation models are supported?

Currently: Free Space Path Loss (FSPL).

Additional losses (atmospheric, rain, polarization) are added separately in the scenario.

### Q: How do Swerling models affect radar detection?

Higher Swerling models represent target fluctuation and require more SNR:

| Model | Typical SNR Penalty |
|-------|---------------------|
| 0 (steady) | 0 dB |
| 1 (slow) | 3-8 dB |
| 2 (fast) | 2-5 dB |

## CLI

### Q: How do I use the CLI?

```bash
# Single evaluation
pasys run config.yaml

# DOE study
pasys doe config.yaml -n 100

# Report
pasys report results.parquet

# Pareto
pasys pareto results.parquet -x cost_usd -y eirp_dbw
```

### Q: Where are results saved?

Default: `./results/results.parquet`

Specify with `-o`:

```bash
pasys doe config.yaml -n 100 -o ./my_study
```

## Visualization

### Q: Plots don't display in my environment

Use non-interactive backend:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Save instead of show
fig.savefig("plot.png", dpi=150)
```

### Q: How do I customize plot styling?

Access matplotlib axes:

```python
fig = pareto_plot(results, x="cost_usd", y="eirp_dbw")
ax = fig.axes[0]
ax.set_xlim([0, 100000])
ax.axhline(y=40, color='r', linestyle='--')
```

## Contributing

### Q: How do I report a bug?

Open an issue at: https://github.com/jman4162/phased-array-systems/issues

Include:
- Python version
- Package version
- Minimal reproducible example
- Error message

### Q: How do I contribute code?

See [CONTRIBUTING.md](https://github.com/jman4162/phased-array-systems/blob/main/CONTRIBUTING.md)

## More Help

- **Documentation**: https://jman4162.github.io/phased-array-systems
- **Issues**: https://github.com/jman4162/phased-array-systems/issues
- **Source**: https://github.com/jman4162/phased-array-systems
