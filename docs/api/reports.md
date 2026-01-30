# Reports API

HTML and Markdown report generation.

## Overview

```python
from phased_array_systems.reports import (
    ReportConfig,
    HTMLReport,
    MarkdownReport,
)
```

## Classes

::: phased_array_systems.reports.generator.ReportConfig
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.reports.html.HTMLReport
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.reports.markdown.MarkdownReport
    options:
      show_root_heading: true
      members_order: source

## Usage Examples

### HTML Report

```python
from phased_array_systems.reports import HTMLReport, ReportConfig
import pandas as pd

# Load results
results = pd.read_parquet("results.parquet")

# Configure report
config = ReportConfig(
    title="Communications Array Trade Study",
    description="Analysis of array configurations for X-band link",
    author="Engineering Team",
    version="1.0",
)

# Generate and save
report = HTMLReport(config)
content = report.generate(results)
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

### Report Configuration

```python
config = ReportConfig(
    title="Q4 Array Trade Study",
    description="""
    Systematic exploration of phased array configurations
    for 100 km X-band communications link.
    """,
    author="RF Engineering",
    version="2.1",
)
```

## Report Contents

Reports automatically include:

### Executive Summary

- Total cases evaluated
- Feasible design count and percentage
- Pareto-optimal design count
- Key metric statistics

### Requirements Verification

- Pass/fail summary by requirement
- Overall compliance rate
- Margin statistics

### Top Designs

- Ranked Pareto-optimal designs
- Key metrics for each design
- Configuration parameters

### Statistics

- Metric distributions (min, max, mean, std)
- Variable ranges
- Correlation highlights

## Customization

### Extending Reports

```python
class CustomHTMLReport(HTMLReport):
    def generate(self, results):
        html = super().generate(results)

        # Add custom section
        custom = "<section><h2>Custom Analysis</h2>...</section>"
        html = html.replace("</body>", f"{custom}</body>")

        return html
```

### Adding Figures

```python
import base64
from io import BytesIO

# Generate figure
fig = pareto_plot(results, x="cost_usd", y="eirp_dbw")

# Convert to base64
buffer = BytesIO()
fig.savefig(buffer, format='png', dpi=150)
buffer.seek(0)
img_data = base64.b64encode(buffer.getvalue()).decode()

# Embed in HTML
img_html = f'<img src="data:image/png;base64,{img_data}" alt="Pareto">'
```

## CLI Usage

```bash
# HTML report (default)
pasys report results.parquet -o report.html

# Markdown report
pasys report results.parquet --format markdown -o report.md

# With title
pasys report results.parquet --title "Q4 Analysis"
```

## See Also

- [User Guide: Reports](../user-guide/reports.md)
- [CLI: report](../cli/report.md)
- [Visualization API](viz.md)
