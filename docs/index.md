# phased-array-systems

<div class="grid-container" markdown>
<div class="feature-card" markdown>
### Requirements-First Design
Every evaluation produces pass/fail results with margins and full traceability to requirements.
</div>
<div class="feature-card" markdown>
### Trade-Space Exploration
DOE generation and Pareto analysis enable systematic exploration of design alternatives.
</div>
<div class="feature-card" markdown>
### Model-Based Workflow
MBSE/MDAO workflow from requirements through architecture to optimized designs.
</div>
<div class="feature-card" markdown>
### Python-Native
Clean Python API with Pydantic validation, type hints, and comprehensive documentation.
</div>
</div>

**phased-array-systems** is a Python package for phased array antenna system design, optimization, and performance visualization. It supports both wireless communications and radar applications.

```python
from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig
from phased_array_systems.scenarios import CommsLinkScenario
from phased_array_systems.evaluate import evaluate_case

# Define your array architecture
arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
)

# Define the operating scenario
scenario = CommsLinkScenario(
    freq_hz=10e9,
    bandwidth_hz=10e6,
    range_m=100e3,
    required_snr_db=10.0,
)

# Evaluate performance
metrics = evaluate_case(arch, scenario)
print(f"EIRP: {metrics['eirp_dbw']:.1f} dBW")
print(f"Link Margin: {metrics['link_margin_db']:.1f} dB")
```

## Key Features

### Communications Link Budget Analysis

Calculate EIRP, received power, SNR, and link margin for point-to-point and satellite links:

- Free space path loss propagation
- Atmospheric and rain loss modeling
- Configurable receiver parameters
- Automatic scan loss compensation

### Radar Detection Analysis

Evaluate radar detection performance with:

- Radar range equation calculations
- Swerling target models (0-4)
- Pulse integration (coherent and non-coherent)
- Detection probability and false alarm rate

### Design of Experiments (DOE)

Systematic design space exploration:

- Latin Hypercube Sampling (LHS)
- Full factorial grid generation
- Random sampling with seed control
- Augmented DOE for adaptive studies

### Pareto Analysis

Multi-objective optimization support:

- Pareto frontier extraction
- Weighted sum and TOPSIS ranking
- Hypervolume quality indicator
- Interactive Pareto plots

### Requirements Verification

Track requirements compliance:

- Define requirements with operators (`>=`, `<=`, `==`)
- Severity levels: must, should, nice-to-have
- Automatic margin calculation
- Pass/fail verification reports

## Workflow

```mermaid
graph LR
    A[Config YAML/JSON] --> B[Pydantic Validation]
    B --> C[Architecture + Scenario]
    C --> D[DOE Generation]
    D --> E[Batch Evaluation]
    E --> F[Requirements Verification]
    F --> G[Pareto Extraction]
    G --> H[Visualization & Reports]
```

The package implements a model-based systems engineering (MBSE) workflow:

1. **Configuration**: Define architecture and scenario in YAML/JSON or Python
2. **DOE Generation**: Create design space with variable bounds, generate samples
3. **Batch Evaluation**: Evaluate all cases with parallel processing
4. **Verification**: Check requirements, compute margins
5. **Pareto Analysis**: Extract optimal designs, rank alternatives
6. **Reporting**: Generate plots and HTML/Markdown reports

## Quick Links

<div class="grid-container" markdown>
<div class="feature-card" markdown>
### [Getting Started](getting-started/installation.md)
Install the package and run your first analysis.
</div>
<div class="feature-card" markdown>
### [User Guide](user-guide/index.md)
Learn how to configure architectures, run trade studies, and analyze results.
</div>
<div class="feature-card" markdown>
### [Tutorials](tutorials/index.md)
Step-by-step guides for common workflows.
</div>
<div class="feature-card" markdown>
### [API Reference](api/index.md)
Complete API documentation for all modules.
</div>
</div>

## Installation

```bash
pip install phased-array-systems
```

For development:

```bash
pip install phased-array-systems[dev,plotting,docs]
```

## License

phased-array-systems is released under the [MIT License](https://opensource.org/licenses/MIT).

## Citation

If you use phased-array-systems in academic work, please cite:

```bibtex
@software{phased_array_systems,
  title = {phased-array-systems: Phased Array Antenna System Design and Optimization},
  author = {John Hodge},
  year = {2026},
  url = {https://github.com/jman4162/phased-array-systems}
}
```
