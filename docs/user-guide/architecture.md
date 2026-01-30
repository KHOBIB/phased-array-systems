# Architecture Configuration

The `Architecture` class is the central configuration object in phased-array-systems. It defines all parameters of a phased array system design.

## Overview

An `Architecture` consists of three main components:

| Component | Class | Description |
|-----------|-------|-------------|
| Array | `ArrayConfig` | Antenna array geometry and parameters |
| RF Chain | `RFChainConfig` | Transmit/receive chain parameters |
| Cost | `CostConfig` | Cost model parameters |

```python
from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    RFChainConfig,
    CostConfig,
)

arch = Architecture(
    array=ArrayConfig(nx=8, ny=8),
    rf=RFChainConfig(tx_power_w_per_elem=1.0),
    cost=CostConfig(cost_per_elem_usd=100.0),
    name="My Design",
)
```

## ArrayConfig

The `ArrayConfig` class defines the antenna array geometry.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `geometry` | str | `"rectangular"` | Array geometry type |
| `nx` | int | Required | Elements in x-direction |
| `ny` | int | Required | Elements in y-direction |
| `dx_lambda` | float | `0.5` | X spacing (wavelengths) |
| `dy_lambda` | float | `0.5` | Y spacing (wavelengths) |
| `scan_limit_deg` | float | `60.0` | Maximum scan angle (degrees) |
| `max_subarray_nx` | int | `8` | Max elements per sub-array (x) |
| `max_subarray_ny` | int | `8` | Max elements per sub-array (y) |
| `enforce_subarray_constraint` | bool | `True` | Enforce power-of-2 sub-arrays |

### Geometry Types

Currently supported:

- `"rectangular"` - Standard rectangular grid
- `"circular"` - Circular aperture
- `"triangular"` - Triangular lattice

### Example

```python
array = ArrayConfig(
    geometry="rectangular",
    nx=16,
    ny=16,
    dx_lambda=0.5,           # Half-wavelength spacing
    dy_lambda=0.5,
    scan_limit_deg=60.0,     # ±60° scan range
    max_subarray_nx=8,       # 8x8 sub-arrays
    max_subarray_ny=8,
    enforce_subarray_constraint=True,
)

print(f"Total elements: {array.n_elements}")  # 256
print(f"Sub-arrays: {array.n_subarrays}")     # 4
```

### Sub-Array Constraints

For practical RF component design, array dimensions must be compatible with sub-array tiling. When `enforce_subarray_constraint=True`:

- Array dimensions (`nx`, `ny`) must be powers of 2 if smaller than `max_subarray_*`
- Array dimensions must be divisible by `max_subarray_*` if larger

Valid configurations:
```python
# Small arrays: nx and ny must be powers of 2
ArrayConfig(nx=4, ny=4)   # OK
ArrayConfig(nx=8, ny=8)   # OK

# Large arrays: must be divisible by max_subarray
ArrayConfig(nx=16, ny=16, max_subarray_nx=8)  # OK (16/8 = 2)
ArrayConfig(nx=24, ny=24, max_subarray_nx=8)  # OK (24/8 = 3)

# Invalid (not power of 2 or not divisible)
ArrayConfig(nx=6, ny=6)   # Error
ArrayConfig(nx=12, ny=12, max_subarray_nx=8)  # Error (12/8 ≠ integer)
```

To disable this constraint:
```python
ArrayConfig(nx=10, ny=10, enforce_subarray_constraint=False)  # OK
```

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `n_elements` | int | Total element count (nx × ny) |
| `subarray_nx` | int | Elements per sub-array (x) |
| `subarray_ny` | int | Elements per sub-array (y) |
| `n_subarrays_x` | int | Number of sub-arrays (x) |
| `n_subarrays_y` | int | Number of sub-arrays (y) |
| `n_subarrays` | int | Total sub-array count |
| `elements_per_subarray` | int | Elements in each sub-array |

## RFChainConfig

The `RFChainConfig` class defines transmit and receive chain parameters.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tx_power_w_per_elem` | float | Required | TX power per element (W) |
| `pa_efficiency` | float | `0.3` | Power amplifier efficiency (0-1) |
| `noise_figure_db` | float | `3.0` | Receiver noise figure (dB) |
| `n_tx_beams` | int | `1` | Number of TX beams |
| `feed_loss_db` | float | `1.0` | Feed network loss (dB) |
| `system_loss_db` | float | `0.0` | Additional system losses (dB) |

### Example

```python
rf = RFChainConfig(
    tx_power_w_per_elem=2.0,   # 2 Watts per element
    pa_efficiency=0.35,        # 35% efficient
    noise_figure_db=4.0,       # 4 dB NF
    n_tx_beams=1,              # Single beam
    feed_loss_db=1.5,          # 1.5 dB feed loss
    system_loss_db=0.5,        # 0.5 dB other losses
)
```

### Power Calculations

Total transmit power:

$$
P_{tx,total} = P_{tx,elem} \times N_{elements}
$$

DC power consumption:

$$
P_{DC} = \frac{P_{tx,total}}{\eta_{PA}}
$$

Where $\eta_{PA}$ is the PA efficiency.

## CostConfig

The `CostConfig` class defines cost model parameters.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cost_per_elem_usd` | float | `100.0` | Recurring cost per element ($) |
| `nre_usd` | float | `0.0` | Non-recurring engineering cost ($) |
| `integration_cost_usd` | float | `0.0` | System integration cost ($) |

### Example

```python
cost = CostConfig(
    cost_per_elem_usd=150.0,     # $150 per element
    nre_usd=50000.0,             # $50k NRE
    integration_cost_usd=10000.0, # $10k integration
)
```

### Cost Calculations

Total recurring cost:

$$
C_{recurring} = C_{elem} \times N_{elements}
$$

Total cost:

$$
C_{total} = C_{recurring} + C_{NRE} + C_{integration}
$$

## Architecture Class

The `Architecture` class combines all components.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `array` | ArrayConfig | Required | Array configuration |
| `rf` | RFChainConfig | Required | RF chain configuration |
| `cost` | CostConfig | `CostConfig()` | Cost configuration |
| `name` | str | `None` | Optional name |

### Example

```python
arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
    cost=CostConfig(cost_per_elem_usd=100.0, nre_usd=10000.0),
    name="8x8 Baseline Design",
)

print(f"Name: {arch.name}")
print(f"Elements: {arch.n_elements}")
```

### Flattening and Reconstruction

For DOE and serialization, architectures can be flattened to/from dictionaries:

```python
# Flatten to dict
flat = arch.model_dump_flat()
# {
#     "array.nx": 8,
#     "array.ny": 8,
#     "array.dx_lambda": 0.5,
#     "rf.tx_power_w_per_elem": 1.0,
#     ...
# }

# Reconstruct from dict
arch2 = Architecture.from_flat(flat)
```

This is used internally by the DOE system to vary parameters.

## Validation

All configurations use Pydantic for validation:

```python
# This raises ValidationError
try:
    ArrayConfig(nx=-1, ny=8)  # nx must be >= 1
except ValueError as e:
    print(e)

try:
    RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=1.5)  # efficiency > 1
except ValueError as e:
    print(e)
```

## YAML Configuration

Architectures can be defined in YAML:

```yaml
# architecture.yaml
array:
  geometry: rectangular
  nx: 8
  ny: 8
  dx_lambda: 0.5
  dy_lambda: 0.5
  scan_limit_deg: 60.0

rf:
  tx_power_w_per_elem: 1.0
  pa_efficiency: 0.3
  noise_figure_db: 3.0
  feed_loss_db: 1.0

cost:
  cost_per_elem_usd: 100.0
  nre_usd: 10000.0
  integration_cost_usd: 5000.0
```

Load with:

```python
from phased_array_systems.io import load_config

config = load_config("architecture.yaml")
arch = config.get_architecture()
```

## Best Practices

### 1. Use Realistic Spacing

Half-wavelength spacing ($d = 0.5\lambda$) is typical:

```python
ArrayConfig(dx_lambda=0.5, dy_lambda=0.5)  # Standard
ArrayConfig(dx_lambda=0.6, dy_lambda=0.6)  # Wider (grating lobes possible)
```

### 2. Consider Sub-Array Constraints Early

Design array dimensions to be compatible with sub-array tiling from the start.

### 3. Document Designs with Names

```python
arch = Architecture(
    ...,
    name="Design_A_16x16_2W",  # Descriptive name
)
```

### 4. Use Type Hints for IDE Support

```python
from phased_array_systems.architecture import Architecture

def analyze_design(arch: Architecture) -> dict:
    """IDE will provide autocomplete for arch."""
    return {"elements": arch.n_elements}
```

## See Also

- [Scenarios](scenarios.md) - Define operating conditions
- [Requirements](requirements.md) - Define design requirements
- [API Reference](../api/architecture.md) - Complete API documentation
