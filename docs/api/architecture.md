# Architecture API

System configuration classes for defining phased array architectures.

## Overview

```python
from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    RFChainConfig,
    CostConfig,
)
```

## Classes

::: phased_array_systems.architecture.config.ArrayConfig
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.architecture.config.RFChainConfig
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.architecture.config.CostConfig
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.architecture.config.Architecture
    options:
      show_root_heading: true
      members_order: source

## Helper Functions

::: phased_array_systems.architecture.config.is_power_of_two
    options:
      show_root_heading: true

## Constants

```python
# Valid sub-array dimensions (powers of 2)
VALID_POWERS_OF_TWO = [2, 4, 8, 16, 32, 64, 128, 256, 512]
```

## Usage Examples

### Basic Architecture

```python
from phased_array_systems.architecture import (
    Architecture, ArrayConfig, RFChainConfig, CostConfig
)

arch = Architecture(
    array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
    rf=RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=0.3),
    cost=CostConfig(cost_per_elem_usd=100.0),
    name="Baseline Design",
)

print(f"Elements: {arch.n_elements}")
print(f"Sub-arrays: {arch.array.n_subarrays}")
```

### Flattening for DOE

```python
# Convert to flat dictionary
flat = arch.model_dump_flat()
# {'array.nx': 8, 'array.ny': 8, 'array.dx_lambda': 0.5, ...}

# Reconstruct from flat dictionary
arch2 = Architecture.from_flat(flat)
```

### Validation Examples

```python
# This raises ValidationError - nx must be >= 1
ArrayConfig(nx=0, ny=8)

# This raises ValidationError - efficiency must be 0-1
RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=1.5)

# This raises ValidationError - not power of 2
ArrayConfig(nx=6, ny=6, enforce_subarray_constraint=True)

# This works - constraint disabled
ArrayConfig(nx=6, ny=6, enforce_subarray_constraint=False)
```

## See Also

- [User Guide: Architecture](../user-guide/architecture.md)
- [Scenarios API](scenarios.md)
- [Requirements API](requirements.md)
