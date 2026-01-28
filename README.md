# phased-array-systems

Phased array antenna system design, optimization, and performance visualization for wireless communications and radar applications.

## Features

- **Requirements as first-class objects**: Every run produces pass/fail + margins with traceability
- **Trade-space exploration**: DOE + Pareto optimization over single-point designs
- **Flat metrics dictionary**: All models return consistent `dict[str, float]` for interchange
- **Config-driven reproducibility**: Stable case IDs, seed control, version stamping

## Installation

```bash
pip install phased-array-systems

# Development dependencies
pip install phased-array-systems[dev]

# Visualization extras
pip install phased-array-systems[plotting]
```

## Quick Start

### Single Case Evaluation

```python
from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig
from phased_array_systems.scenarios import CommsLinkScenario
from phased_array_systems.evaluate import evaluate_case

# Define architecture
arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
)

# Define scenario
scenario = CommsLinkScenario(
    freq_hz=10e9,
    bandwidth_hz=10e6,
    range_m=100e3,
    required_snr_db=10.0,
)

# Evaluate
metrics = evaluate_case(arch, scenario)
print(f"EIRP: {metrics['eirp_dbw']:.1f} dBW")
print(f"Link Margin: {metrics['link_margin_db']:.1f} dB")
```

### DOE Trade Study

```python
from phased_array_systems.trades import DesignSpace, generate_doe, BatchRunner, extract_pareto

# Define design space
space = (
    DesignSpace()
    .add_variable("array.nx", "int", low=4, high=16)
    .add_variable("array.ny", "int", low=4, high=16)
    .add_variable("rf.tx_power_w_per_elem", "float", low=0.5, high=3.0)
)

# Generate DOE
doe = generate_doe(space, method="lhs", n_samples=100, seed=42)

# Run batch evaluation
runner = BatchRunner(scenario)
results = runner.run(doe)

# Extract Pareto frontier
pareto = extract_pareto(results, [
    ("cost_usd", "minimize"),
    ("eirp_dbw", "maximize"),
])
```

## Examples

See the `examples/` directory:
- `01_comms_single_case.py` - Single case evaluation
- `02_comms_doe_trade.py` - Full DOE trade study workflow

## Project Status

Currently in development. See `CLAUDE.md` for implementation phases.

## License

MIT
