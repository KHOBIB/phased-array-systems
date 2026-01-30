# Requirements

Requirements are first-class objects in phased-array-systems, enabling systematic tracking of design compliance with automatic verification and margin calculation.

## Overview

The requirements system provides:

- **Definition**: Specify requirements with thresholds and operators
- **Verification**: Automatic pass/fail checking against metrics
- **Margins**: Quantify how much margin exists (positive or negative)
- **Traceability**: Link results back to requirement IDs

## Defining Requirements

### Single Requirement

```python
from phased_array_systems.requirements import Requirement

req = Requirement(
    id="REQ-001",           # Unique identifier
    name="Minimum EIRP",     # Human-readable name
    metric_key="eirp_dbw",   # Key in metrics dictionary
    op=">=",                 # Comparison operator
    value=40.0,              # Threshold value
    units="dBW",             # Optional units (documentation)
    severity="must",         # Importance level
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | str | Yes | Unique identifier (e.g., "REQ-001") |
| `name` | str | Yes | Human-readable description |
| `metric_key` | str | Yes | Key to check in metrics dict |
| `op` | str | Yes | Comparison operator |
| `value` | float | Yes | Threshold value |
| `units` | str | No | Units for documentation |
| `severity` | str | No | "must", "should", or "nice" |

### Operators

| Operator | Meaning | Passes When |
|----------|---------|-------------|
| `>=` | Greater or equal | metric >= value |
| `<=` | Less or equal | metric <= value |
| `>` | Greater than | metric > value |
| `<` | Less than | metric < value |
| `==` | Equal to | metric == value |

### Severity Levels

| Level | Meaning | Verification Impact |
|-------|---------|---------------------|
| `"must"` | Mandatory | Fails overall if not met |
| `"should"` | Desired | Tracked but doesn't fail |
| `"nice"` | Optional | Tracked but doesn't fail |

## RequirementSet

Group requirements together for verification:

```python
from phased_array_systems.requirements import RequirementSet

requirements = RequirementSet(
    requirements=[
        Requirement("REQ-001", "Min EIRP", "eirp_dbw", ">=", 40.0, severity="must"),
        Requirement("REQ-002", "Positive Margin", "link_margin_db", ">=", 0.0, severity="must"),
        Requirement("REQ-003", "Max Cost", "cost_usd", "<=", 50000.0, severity="must"),
        Requirement("REQ-004", "Target EIRP", "eirp_dbw", ">=", 45.0, severity="should"),
    ],
    name="Communications Requirements",
)
```

## Verification

### Basic Verification

```python
from phased_array_systems.evaluate import evaluate_case

# Evaluate design
metrics = evaluate_case(arch, scenario)

# Verify requirements
report = requirements.verify(metrics)

# Check overall status
print(f"Overall: {'PASS' if report.passes else 'FAIL'}")
```

### VerificationReport

The `verify()` method returns a `VerificationReport`:

```python
report = requirements.verify(metrics)

# Summary counts
print(f"Must: {report.must_pass_count}/{report.must_total_count}")
print(f"Should: {report.should_pass_count}/{report.should_total_count}")

# Failed requirement IDs
if report.failed_ids:
    print(f"Failed: {report.failed_ids}")

# Individual results
for result in report.results:
    status = "PASS" if result.passes else "FAIL"
    print(f"{result.requirement.id}: {status}")
    print(f"  Actual: {result.actual_value:.2f}")
    print(f"  Threshold: {result.requirement.value:.2f}")
    print(f"  Margin: {result.margin:.2f}")
```

### Margin Calculation

Margins indicate how much room exists:

- **Positive margin**: Requirement is satisfied with room to spare
- **Zero margin**: Exactly at threshold
- **Negative margin**: Requirement is not met

For different operators:

| Operator | Margin Formula |
|----------|---------------|
| `>=`, `>` | actual - threshold |
| `<=`, `<` | threshold - actual |
| `==` | -abs(actual - threshold) |

```python
# Example: EIRP >= 40 dBW with actual = 45 dBW
# Margin = 45 - 40 = 5 dB (passes with 5 dB margin)

# Example: Cost <= 50000 with actual = 45000
# Margin = 50000 - 45000 = 5000 (passes with $5k margin)
```

## Integration with Batch Evaluation

Requirements integrate with the trade study workflow:

```python
from phased_array_systems.trades import BatchRunner, filter_feasible

# Create runner with requirements
runner = BatchRunner(scenario, requirements)

# Run batch - results include verification columns
results = runner.run(doe)

# Results DataFrame includes:
# - verification.passes (1.0 or 0.0)
# - verification.must_pass_count
# - verification.must_total_count
# - verification.margin_* for each requirement

# Filter to feasible only
feasible = filter_feasible(results, requirements)
```

### Verification Columns

After batch evaluation, the results DataFrame includes:

| Column | Description |
|--------|-------------|
| `verification.passes` | 1.0 if all must requirements pass |
| `verification.must_pass_count` | Number of must requirements passed |
| `verification.must_total_count` | Total must requirements |
| `verification.should_pass_count` | Should requirements passed |
| `verification.should_total_count` | Total should requirements |

## Common Requirement Patterns

### Communications Link

```python
comms_requirements = RequirementSet(requirements=[
    # Performance
    Requirement("LINK-001", "Min EIRP", "eirp_dbw", ">=", 40.0, severity="must"),
    Requirement("LINK-002", "Positive Margin", "link_margin_db", ">=", 0.0, severity="must"),
    Requirement("LINK-003", "3dB Margin", "link_margin_db", ">=", 3.0, severity="should"),

    # SWaP-C
    Requirement("SWAP-001", "Max Cost", "cost_usd", "<=", 100000.0, severity="must"),
    Requirement("SWAP-002", "Max Power", "prime_power_w", "<=", 1000.0, severity="must"),

    # Antenna
    Requirement("ANT-001", "Min Gain", "g_peak_db", ">=", 25.0, severity="should"),
])
```

### Radar Detection

```python
radar_requirements = RequirementSet(requirements=[
    # Detection
    Requirement("DET-001", "Positive SNR Margin", "snr_margin_db", ">=", 0.0, severity="must"),
    Requirement("DET-002", "5dB SNR Margin", "snr_margin_db", ">=", 5.0, severity="should"),

    # Range
    Requirement("RNG-001", "Min Range", "detection_range_m", ">=", 100e3, severity="must"),

    # SWaP-C
    Requirement("SWAP-001", "Max Cost", "cost_usd", "<=", 500000.0, severity="must"),
])
```

## YAML Configuration

Requirements can be defined in YAML:

```yaml
requirements:
  - id: REQ-001
    name: Minimum EIRP
    metric_key: eirp_dbw
    op: ">="
    value: 40.0
    units: dBW
    severity: must

  - id: REQ-002
    name: Positive Link Margin
    metric_key: link_margin_db
    op: ">="
    value: 0.0
    units: dB
    severity: must

  - id: REQ-003
    name: Maximum Cost
    metric_key: cost_usd
    op: "<="
    value: 50000.0
    units: USD
    severity: must
```

Load with:

```python
from phased_array_systems.io import load_config

config = load_config("config.yaml")
requirements = config.get_requirement_set()
```

## Serialization

### To Dictionary

```python
report = requirements.verify(metrics)
report_dict = report.to_dict()

# Contains:
# {
#     "passes": True,
#     "failed_ids": [],
#     "must_pass_count": 3,
#     "must_total_count": 3,
#     "results": [
#         {
#             "id": "REQ-001",
#             "name": "Minimum EIRP",
#             "metric_key": "eirp_dbw",
#             "threshold": 40.0,
#             "operator": ">=",
#             "actual_value": 45.0,
#             "passes": True,
#             "margin": 5.0,
#             "severity": "must",
#         },
#         ...
#     ]
# }
```

### Export to Report

The report generators include requirement verification:

```python
from phased_array_systems.reports import HTMLReport, ReportConfig

report_gen = HTMLReport(ReportConfig(title="Trade Study"))
html = report_gen.generate(results)
# Includes requirement pass/fail summary and margins
```

## Best Practices

### 1. Use Meaningful IDs

Organize IDs by category:

```python
Requirement("PERF-001", ...)  # Performance
Requirement("SWAP-001", ...)  # Size, Weight, Power, Cost
Requirement("ANT-001", ...)   # Antenna
Requirement("LINK-001", ...)  # Link budget
```

### 2. Define Both Minimum and Target

```python
RequirementSet(requirements=[
    Requirement("EIRP-MIN", "Min EIRP", "eirp_dbw", ">=", 40.0, severity="must"),
    Requirement("EIRP-TGT", "Target EIRP", "eirp_dbw", ">=", 45.0, severity="should"),
])
```

### 3. Include Units for Documentation

```python
Requirement(
    ...,
    units="dBW",  # Helps with report clarity
)
```

### 4. Use Severity Appropriately

- `"must"`: Hard constraints that must be met
- `"should"`: Important goals but not showstoppers
- `"nice"`: Stretch goals for optimization

## See Also

- [Architecture Configuration](architecture.md) - Define system parameters
- [Trade Studies](trade-studies.md) - Batch evaluation with requirements
- [API Reference](../api/requirements.md) - Complete API documentation
