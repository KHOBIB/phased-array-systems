# Report Generation

phased-array-systems can generate HTML and Markdown reports summarizing trade study results.

## Overview

Reports include:

- Executive summary with key statistics
- Requirements verification summary
- Pareto frontier analysis
- Design space exploration metrics
- Top design recommendations

## Report Types

| Type | Class | Output |
|------|-------|--------|
| HTML | `HTMLReport` | Standalone HTML file |
| Markdown | `MarkdownReport` | Markdown text file |

## Basic Usage

### HTML Report

```python
from phased_array_systems.reports import HTMLReport, ReportConfig
import pandas as pd

# Load results
results = pd.read_parquet("results.parquet")

# Configure report
config = ReportConfig(
    title="Communications Array Trade Study",
)

# Generate HTML
report = HTMLReport(config)
content = report.generate(results)

# Save
report.save(content, "report.html")
```

### Markdown Report

```python
from phased_array_systems.reports import MarkdownReport, ReportConfig

config = ReportConfig(title="Trade Study Summary")
report = MarkdownReport(config)
content = report.generate(results)
report.save(content, "report.md")
```

## ReportConfig

Configure report generation:

```python
from phased_array_systems.reports import ReportConfig

config = ReportConfig(
    title="My Trade Study",
    description="Analysis of array configurations for X-band communications",
    author="Engineering Team",
    version="1.0",
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | str | "Trade Study Report" | Report title |
| `description` | str | None | Optional description |
| `author` | str | None | Author name |
| `version` | str | None | Report version |

## CLI Usage

Generate reports from the command line:

```bash
# HTML report (default)
pasys report results.parquet -o report.html

# Markdown report
pasys report results.parquet --format markdown -o report.md

# Custom title
pasys report results.parquet --title "Q4 Trade Study"
```

## Report Contents

### Executive Summary

- Total cases evaluated
- Feasible designs count and percentage
- Pareto-optimal design count
- Key metric ranges (min, max, mean)

### Requirements Verification

- Pass/fail summary
- Requirement-by-requirement status
- Margin statistics

### Pareto Analysis

- Number of Pareto-optimal designs
- Objective trade-offs
- Top recommended designs

### Design Statistics

- Design variable distributions
- Output metric statistics
- Correlation highlights

## Customizing Reports

### Adding Figures

Generate and embed figures in reports:

```python
from phased_array_systems.viz import pareto_plot
from phased_array_systems.trades import extract_pareto
import base64
from io import BytesIO

# Generate figure
pareto = extract_pareto(results, [("cost_usd", "minimize"), ("eirp_dbw", "maximize")])
fig = pareto_plot(results, x="cost_usd", y="eirp_dbw", pareto_front=pareto)

# Convert to base64 for HTML embedding
buffer = BytesIO()
fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
img_data = base64.b64encode(buffer.getvalue()).decode()

# Use in custom HTML
html_img = f'<img src="data:image/png;base64,{img_data}" alt="Pareto Plot">'
```

### Custom Sections

Extend the base report classes:

```python
from phased_array_systems.reports import HTMLReport, ReportConfig

class CustomHTMLReport(HTMLReport):
    def generate(self, results):
        # Call parent
        html = super().generate(results)

        # Add custom section before closing body
        custom_section = """
        <section>
            <h2>Custom Analysis</h2>
            <p>Additional project-specific content...</p>
        </section>
        """
        html = html.replace("</body>", f"{custom_section}</body>")

        return html
```

## Complete Example

```python
"""Generate comprehensive trade study report."""

import pandas as pd
from pathlib import Path

from phased_array_systems.reports import HTMLReport, MarkdownReport, ReportConfig
from phased_array_systems.trades import filter_feasible, extract_pareto, rank_pareto
from phased_array_systems.viz import pareto_plot, scatter_matrix

# Load results
results = pd.read_parquet("results.parquet")
print(f"Loaded {len(results)} cases")

# Analysis
feasible = filter_feasible(results)
objectives = [("cost_usd", "minimize"), ("eirp_dbw", "maximize")]
pareto = extract_pareto(feasible, objectives)
ranked = rank_pareto(pareto, objectives)

print(f"Feasible: {len(feasible)} ({len(feasible)/len(results)*100:.1f}%)")
print(f"Pareto-optimal: {len(pareto)}")

# Create output directory
output_dir = Path("./report")
output_dir.mkdir(exist_ok=True)

# Generate figures
fig1 = pareto_plot(
    results, x="cost_usd", y="eirp_dbw",
    pareto_front=pareto,
    feasible_mask=results["verification.passes"] == 1.0,
    title="Cost vs EIRP Trade Space",
)
fig1.savefig(output_dir / "pareto.png", dpi=150, bbox_inches="tight")

fig2 = scatter_matrix(
    feasible,
    columns=["cost_usd", "eirp_dbw", "link_margin_db"],
    title="Key Metrics Correlation",
)
fig2.savefig(output_dir / "scatter.png", dpi=150, bbox_inches="tight")

# Generate HTML report
config = ReportConfig(
    title="Communications Array Trade Study",
    description="Systematic exploration of array configurations for X-band link",
    author="Engineering Team",
    version="1.0",
)

html_report = HTMLReport(config)
html_content = html_report.generate(results)
html_report.save(html_content, output_dir / "report.html")
print(f"HTML report: {output_dir / 'report.html'}")

# Generate Markdown report
md_report = MarkdownReport(config)
md_content = md_report.generate(results)
md_report.save(md_content, output_dir / "report.md")
print(f"Markdown report: {output_dir / 'report.md'}")

# Export supporting data
from phased_array_systems.io import export_results
export_results(ranked, output_dir / "pareto_ranked.csv", format="csv")
print(f"Pareto data: {output_dir / 'pareto_ranked.csv'}")
```

## Report Template Structure

### HTML Report Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>/* Embedded CSS */</style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p>{description}</p>
        <p>Generated: {timestamp}</p>
    </header>

    <section id="summary">
        <h2>Executive Summary</h2>
        <!-- Statistics -->
    </section>

    <section id="requirements">
        <h2>Requirements Verification</h2>
        <!-- Pass/fail table -->
    </section>

    <section id="pareto">
        <h2>Pareto Analysis</h2>
        <!-- Top designs -->
    </section>

    <section id="statistics">
        <h2>Design Statistics</h2>
        <!-- Metric tables -->
    </section>

    <footer>
        <p>Generated by phased-array-systems v{version}</p>
    </footer>
</body>
</html>
```

### Markdown Report Structure

```markdown
# {title}

{description}

Generated: {timestamp}

## Executive Summary

- Total cases: X
- Feasible: Y (Z%)
- Pareto-optimal: W

## Requirements Verification

| ID | Name | Pass Rate |
|----|------|-----------|
| ... | ... | ... |

## Top Designs

| Rank | Case ID | Cost | EIRP | Margin |
|------|---------|------|------|--------|
| ... | ... | ... | ... | ... |

## Statistics

...

---
*Generated by phased-array-systems*
```

## Integration with Notebooks

Generate reports within Jupyter notebooks:

```python
from IPython.display import HTML, Markdown

# Display HTML inline
html_content = html_report.generate(results)
HTML(html_content)

# Display Markdown inline
md_content = md_report.generate(results)
Markdown(md_content)
```

## Tips

### 1. Include Context

Add description explaining the study:

```python
config = ReportConfig(
    title="Phase 2 Array Trade Study",
    description="""
    Analysis of 8x8 to 32x32 array configurations for 100 km X-band link.
    Objectives: Minimize cost while meeting 35 dBW EIRP requirement.
    """,
)
```

### 2. Version Reports

Track report versions:

```python
config = ReportConfig(
    title="Trade Study",
    version="1.2",  # Update when study changes
)
```

### 3. Archive with Data

Keep reports with their source data:

```
results/
├── study_001/
│   ├── results.parquet
│   ├── pareto.csv
│   ├── report.html
│   └── figures/
│       ├── pareto.png
│       └── scatter.png
```

## See Also

- [Trade Studies](trade-studies.md) - Generate results
- [Visualization](visualization.md) - Create figures
- [CLI Reference](../cli/report.md) - Command-line usage
- [API Reference](../api/reports.md) - Full API documentation
