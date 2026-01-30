# Communications Models API

Link budget calculations for communications systems.

## Overview

```python
from phased_array_systems.models.comms import CommsLinkModel, compute_fspl

# For direct link margin calculations
from phased_array_systems.models.comms.link_budget import compute_link_margin
```

## Classes

::: phased_array_systems.models.comms.link_budget.CommsLinkModel
    options:
      show_root_heading: true
      members_order: source

## Functions

::: phased_array_systems.models.comms.link_budget.compute_link_margin
    options:
      show_root_heading: true

::: phased_array_systems.models.comms.propagation.compute_fspl
    options:
      show_root_heading: true

## Output Metrics

| Metric | Units | Description |
|--------|-------|-------------|
| `tx_power_total_dbw` | dBW | Total TX power |
| `tx_power_per_elem_dbw` | dBW | TX power per element |
| `g_tx_db` | dB | Transmit antenna gain |
| `eirp_dbw` | dBW | Effective isotropic radiated power |
| `path_loss_db` | dB | Total path loss |
| `fspl_db` | dB | Free space path loss only |
| `g_rx_db` | dB | Receive antenna gain |
| `rx_power_dbw` | dBW | Received signal power |
| `noise_power_dbw` | dBW | Receiver noise power |
| `snr_rx_db` | dB | Received SNR |
| `link_margin_db` | dB | Margin above required SNR |
| `required_snr_db` | dB | Required SNR |

## Usage Examples

### Using CommsLinkModel

```python
from phased_array_systems.models.comms.link_budget import CommsLinkModel

model = CommsLinkModel()

# Without pre-computed antenna gain
metrics = model.evaluate(arch, scenario, context={})

# With pre-computed antenna gain
context = {
    "g_peak_db": 28.0,
    "scan_loss_db": 2.5,
}
metrics = model.evaluate(arch, scenario, context)
```

### Quick Link Margin Calculation

```python
from phased_array_systems.models.comms.link_budget import compute_link_margin

result = compute_link_margin(
    eirp_dbw=50.0,
    path_loss_db=160.0,
    g_rx_db=30.0,
    noise_temp_k=290.0,
    bandwidth_hz=10e6,
    noise_figure_db=3.0,
    required_snr_db=10.0,
)

print(f"SNR: {result['snr_db']:.1f} dB")
print(f"Margin: {result['margin_db']:.1f} dB")
```

### Free Space Path Loss

```python
from phased_array_systems.models.comms.propagation import compute_fspl

# At 10 GHz, 100 km
loss = compute_fspl(freq_hz=10e9, range_m=100e3)
print(f"FSPL: {loss:.1f} dB")  # ~152.4 dB
```

## Link Budget Equations

### EIRP

\\[
EIRP = P_{tx} + G_{tx} - L_{tx}
\\]

### Path Loss

\\[
L_{path} = L_{FSPL} + L_{atm} + L_{rain} + L_{pol}
\\]

### Free Space Path Loss

\\[
L_{FSPL} = 20 \log_{10}\left(\frac{4\pi d f}{c}\right)
\\]

### Received Power

\\[
P_{rx} = EIRP - L_{path} + G_{rx}
\\]

### Noise Power

\\[
N = 10 \log_{10}(kTB) + NF
\\]

### SNR and Margin

\\[
SNR = P_{rx} - N
\\]
\\[
Margin = SNR - SNR_{required}
\\]

## See Also

- [Theory: Link Budget Equations](../../theory/link-budget-equations.md)
- [User Guide: Link Budget](../../user-guide/link-budget.md)
- [Scenarios API](../scenarios.md)
