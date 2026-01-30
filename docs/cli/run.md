# pasys run

Evaluate a single configuration case.

## Synopsis

```bash
pasys run <config> [options]
```

## Description

The `run` command evaluates a single architecture/scenario configuration and displays the resulting metrics. This is useful for quick checks and debugging configurations.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `config` | Yes | Path to configuration file (YAML or JSON) |

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | None | Save results to file |
| `--format` | | `table` | Output format: `table`, `json`, `yaml` |

## Output Formats

### Table (default)

Human-readable grouped output:

```bash
pasys run config.yaml
```

```
Results for config.yaml
============================================================

Antenna:
  g_peak_db: 24.0821
  beamwidth_az_deg: 12.5000
  beamwidth_el_deg: 12.5000

Link Budget:
  eirp_dbw: 45.0821
  path_loss_db: 152.4426
  snr_rx_db: 17.0395
  link_margin_db: 7.0395

Cost:
  cost_usd: 21,400.0
  recurring_cost_usd: 6,400.0

Power:
  rf_power_w: 64.0000
  dc_power_w: 213.3333
  prime_power_w: 213.3333

Metadata:
  meta.case_id: single_case
  meta.runtime_s: 0.0123
```

### JSON

Machine-readable JSON:

```bash
pasys run config.yaml --format json
```

```json
{
  "g_peak_db": 24.082,
  "eirp_dbw": 45.082,
  "path_loss_db": 152.443,
  "link_margin_db": 7.040,
  "cost_usd": 21400.0,
  "meta.case_id": "single_case"
}
```

### YAML

YAML output:

```bash
pasys run config.yaml --format yaml
```

```yaml
g_peak_db: 24.082
eirp_dbw: 45.082
path_loss_db: 152.443
link_margin_db: 7.040
cost_usd: 21400.0
```

## Saving Results

```bash
# Save to JSON file
pasys run config.yaml -o results.json

# Results are always saved as JSON
```

## Examples

### Basic Evaluation

```bash
pasys run config.yaml
```

### JSON Output for Scripting

```bash
# Extract specific metric
pasys run config.yaml --format json | jq '.link_margin_db'

# Check if passes threshold
MARGIN=$(pasys run config.yaml --format json | jq '.link_margin_db')
if (( $(echo "$MARGIN > 0" | bc -l) )); then
  echo "Link closes!"
fi
```

### Save and Display

```bash
pasys run config.yaml --format table -o results.json
# Displays table AND saves JSON
```

## Configuration Requirements

The configuration file must include:

- `architecture` section with `array` and `rf`
- `scenario` section with scenario parameters

Optional:
- `requirements` section for verification

```yaml
# Minimal config.yaml
architecture:
  array:
    nx: 8
    ny: 8
  rf:
    tx_power_w_per_elem: 1.0

scenario:
  type: comms
  freq_hz: 10.0e9
  bandwidth_hz: 10.0e6
  range_m: 100.0e3
  required_snr_db: 10.0
```

## Error Handling

```bash
# File not found
pasys run missing.yaml
# Error: Config file not found: missing.yaml

# Invalid configuration
pasys run invalid.yaml
# Error: validation error for ArrayConfig
#   nx: Input should be greater than or equal to 1
```

## See Also

- [pasys doe](doe.md) - Batch DOE evaluation
- [I/O API](../api/io.md) - Configuration schema
