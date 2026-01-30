# Visualization

phased-array-systems provides plotting functions for trade study visualization using matplotlib.

## Overview

Available plot types:

| Function | Description |
|----------|-------------|
| `pareto_plot` | 2D trade-off with Pareto frontier |
| `scatter_matrix` | Pairwise relationships |
| `trade_space_plot` | 3D trade space |
| `save_figure` | Export to file |

## Pareto Plot

Visualize trade-offs between two objectives with Pareto frontier highlighted.

### Basic Usage

```python
from phased_array_systems.viz import pareto_plot

fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
)
fig.savefig("pareto.png", dpi=150)
```

### With Pareto Frontier

```python
from phased_array_systems.trades import extract_pareto

pareto = extract_pareto(results, [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
])

fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
)
```

### With Feasibility

```python
# Create feasibility mask
feasible_mask = results["verification.passes"] == 1.0

fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
    feasible_mask=feasible_mask,  # Infeasible shown as gray X
)
```

### With Color Mapping

```python
fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
    color_by="link_margin_db",  # Color by a third metric
)
```

### With Size Mapping

```python
fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    size_by="n_elements",  # Size by element count
)
```

### Full Options

```python
fig = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto,
    feasible_mask=feasible_mask,
    color_by="link_margin_db",
    size_by="n_elements",
    ax=None,                     # Use existing axes
    title="Cost vs EIRP Trade Space",
    x_label="Total Cost (USD)",
    y_label="EIRP (dBW)",
    show_pareto_line=True,       # Connect Pareto points
    figsize=(10, 8),
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `results` | DataFrame | Evaluation results |
| `x` | str | Column for x-axis |
| `y` | str | Column for y-axis |
| `pareto_front` | DataFrame | Pareto-optimal points |
| `feasible_mask` | Series | Boolean mask for feasibility |
| `color_by` | str | Column for color mapping |
| `size_by` | str | Column for size mapping |
| `ax` | Axes | Existing axes to use |
| `title` | str | Plot title |
| `x_label` | str | X-axis label |
| `y_label` | str | Y-axis label |
| `show_pareto_line` | bool | Draw line through Pareto points |
| `figsize` | tuple | Figure size (width, height) |

## Scatter Matrix

Visualize pairwise relationships between multiple metrics.

### Basic Usage

```python
from phased_array_systems.viz import scatter_matrix

fig = scatter_matrix(
    results,
    columns=["cost_usd", "eirp_dbw", "link_margin_db", "prime_power_w"],
)
fig.savefig("scatter_matrix.png", dpi=150)
```

### With Color Mapping

```python
fig = scatter_matrix(
    results,
    columns=["cost_usd", "eirp_dbw", "link_margin_db"],
    color_by="n_elements",
)
```

### Diagonal Options

```python
# Histogram on diagonal (default)
fig = scatter_matrix(results, columns=columns, diagonal="hist")

# Kernel density estimate on diagonal
fig = scatter_matrix(results, columns=columns, diagonal="kde")
```

### Full Options

```python
fig = scatter_matrix(
    feasible,                    # Use feasible designs only
    columns=["cost_usd", "eirp_dbw", "link_margin_db", "prime_power_w"],
    color_by="n_elements",
    diagonal="hist",             # "hist" or "kde"
    figsize=(12, 12),
    title="Trade Space Scatter Matrix",
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `results` | DataFrame | Evaluation results |
| `columns` | list[str] | Columns to include |
| `color_by` | str | Column for color mapping |
| `diagonal` | str | "hist" or "kde" |
| `figsize` | tuple | Figure size |
| `title` | str | Overall title |

## 3D Trade Space Plot

Visualize three objectives simultaneously.

### Basic Usage

```python
from phased_array_systems.viz import trade_space_plot

fig = trade_space_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    z="prime_power_w",
)
```

### With Pareto Frontier

```python
# 3-objective Pareto
pareto = extract_pareto(feasible, [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
    ("prime_power_w", "minimize"),
])

fig = trade_space_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    z="prime_power_w",
    pareto_front=pareto,
)
```

### Full Options

```python
fig = trade_space_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    z="prime_power_w",
    feasible_mask=feasible_mask,
    pareto_front=pareto,
    ax=None,                     # Use existing 3D axes
    figsize=(10, 8),
    title="3D Trade Space",
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `results` | DataFrame | Evaluation results |
| `x` | str | Column for x-axis |
| `y` | str | Column for y-axis |
| `z` | str | Column for z-axis (also color) |
| `feasible_mask` | Series | Boolean mask |
| `pareto_front` | DataFrame | Pareto-optimal points |
| `ax` | Axes3D | Existing 3D axes |
| `figsize` | tuple | Figure size |
| `title` | str | Plot title |

## Saving Figures

### Using save_figure

```python
from phased_array_systems.viz import save_figure

fig = pareto_plot(results, x="cost_usd", y="eirp_dbw")

# PNG (default)
save_figure(fig, "plot.png", dpi=150)

# PDF (vector)
save_figure(fig, "plot.pdf")

# SVG
save_figure(fig, "plot.svg")

# Transparent background
save_figure(fig, "plot.png", transparent=True)
```

### Using matplotlib directly

```python
fig.savefig("plot.png", dpi=150, bbox_inches="tight")
```

## Custom Styling

### Using Existing Axes

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot on specific axes
pareto_plot(results, x="cost_usd", y="eirp_dbw", ax=axes[0])
pareto_plot(results, x="cost_usd", y="link_margin_db", ax=axes[1])

fig.tight_layout()
fig.savefig("combined.png", dpi=150)
```

### Post-Processing

```python
fig = pareto_plot(results, x="cost_usd", y="eirp_dbw")
ax = fig.axes[0]

# Add annotations
ax.annotate(
    "Best Design",
    xy=(best_cost, best_eirp),
    xytext=(best_cost + 5000, best_eirp + 2),
    arrowprops=dict(arrowstyle="->"),
)

# Add reference lines
ax.axhline(y=40, color='r', linestyle='--', label='Min EIRP Req')
ax.axvline(x=50000, color='g', linestyle='--', label='Budget Limit')

ax.legend()
fig.savefig("annotated.png", dpi=150)
```

## Complete Example

```python
"""Comprehensive visualization example."""

import matplotlib.pyplot as plt
from phased_array_systems.viz import pareto_plot, scatter_matrix, trade_space_plot, save_figure
from phased_array_systems.trades import filter_feasible, extract_pareto

# Filter and extract Pareto
feasible = filter_feasible(results, requirements)
feasible_mask = results["verification.passes"] == 1.0

pareto_2d = extract_pareto(feasible, [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
])

pareto_3d = extract_pareto(feasible, [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
    ("prime_power_w", "minimize"),
])

# Create output directory
from pathlib import Path
output_dir = Path("./figures")
output_dir.mkdir(exist_ok=True)

# 1. Main Pareto plot
fig1 = pareto_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    pareto_front=pareto_2d,
    feasible_mask=feasible_mask,
    color_by="link_margin_db",
    title="Cost vs EIRP Trade Space",
    x_label="Total Cost (USD)",
    y_label="EIRP (dBW)",
)
save_figure(fig1, output_dir / "pareto_cost_eirp.png", dpi=150)

# 2. Alternative Pareto view
fig2 = pareto_plot(
    results,
    x="cost_usd",
    y="link_margin_db",
    pareto_front=extract_pareto(feasible, [
        ("cost_usd", "minimize"),
        ("link_margin_db", "maximize"),
    ]),
    feasible_mask=feasible_mask,
    title="Cost vs Link Margin",
)
save_figure(fig2, output_dir / "pareto_cost_margin.png", dpi=150)

# 3. Scatter matrix
fig3 = scatter_matrix(
    feasible,
    columns=["cost_usd", "eirp_dbw", "link_margin_db", "prime_power_w", "n_elements"],
    color_by="array.nx",
    diagonal="hist",
    title="Trade Space Correlations (Feasible Designs)",
    figsize=(14, 14),
)
save_figure(fig3, output_dir / "scatter_matrix.png", dpi=150)

# 4. 3D trade space
fig4 = trade_space_plot(
    results,
    x="cost_usd",
    y="eirp_dbw",
    z="prime_power_w",
    feasible_mask=feasible_mask,
    pareto_front=pareto_3d,
    title="3D Trade Space (Cost, EIRP, Power)",
)
save_figure(fig4, output_dir / "trade_space_3d.png", dpi=150)

# 5. Multi-panel figure
fig5, axes = plt.subplots(2, 2, figsize=(14, 12))

pareto_plot(results, x="cost_usd", y="eirp_dbw",
            pareto_front=pareto_2d, feasible_mask=feasible_mask, ax=axes[0, 0],
            title="Cost vs EIRP")

pareto_plot(results, x="cost_usd", y="link_margin_db",
            feasible_mask=feasible_mask, ax=axes[0, 1],
            title="Cost vs Margin")

pareto_plot(results, x="n_elements", y="eirp_dbw",
            feasible_mask=feasible_mask, ax=axes[1, 0],
            title="Array Size vs EIRP")

pareto_plot(results, x="prime_power_w", y="eirp_dbw",
            feasible_mask=feasible_mask, ax=axes[1, 1],
            title="Power vs EIRP")

fig5.tight_layout()
save_figure(fig5, output_dir / "multi_panel.png", dpi=150)

plt.close("all")
print(f"Figures saved to {output_dir}")
```

## Tips

### 1. Use Consistent Coloring

```python
# Same color_by across plots for consistency
for x_metric in ["cost_usd", "prime_power_w", "n_elements"]:
    fig = pareto_plot(
        results, x=x_metric, y="eirp_dbw",
        color_by="link_margin_db",  # Consistent coloring
    )
```

### 2. Close Figures

```python
plt.close("all")  # Prevent memory issues with many plots
```

### 3. Non-Interactive Backend

For scripts without display:

```python
import matplotlib
matplotlib.use("Agg")  # Before importing pyplot
import matplotlib.pyplot as plt
```

### 4. High-Quality Export

```python
# For publications
fig.savefig("plot.pdf", dpi=300, bbox_inches="tight")

# For presentations
fig.savefig("plot.png", dpi=150, transparent=True)
```

## See Also

- [Trade Studies](trade-studies.md) - Generate results to visualize
- [Pareto Analysis](pareto-analysis.md) - Extract Pareto frontiers
- [Reports](reports.md) - Generate HTML reports with embedded figures
- [API Reference](../api/viz.md) - Full API documentation
