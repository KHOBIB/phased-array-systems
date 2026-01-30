# Requirements API

Requirements definition and verification classes.

## Overview

```python
from phased_array_systems.requirements import (
    Requirement,
    RequirementResult,
    RequirementSet,
    VerificationReport,
)
```

## Classes

::: phased_array_systems.requirements.core.Requirement
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.requirements.core.RequirementResult
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.requirements.core.RequirementSet
    options:
      show_root_heading: true
      members_order: source

::: phased_array_systems.requirements.core.VerificationReport
    options:
      show_root_heading: true
      members_order: source

## Usage Examples

### Defining Requirements

```python
from phased_array_systems.requirements import Requirement, RequirementSet

# Create individual requirements
req1 = Requirement(
    id="REQ-001",
    name="Minimum EIRP",
    metric_key="eirp_dbw",
    op=">=",
    value=40.0,
    units="dBW",
    severity="must",
)

req2 = Requirement(
    id="REQ-002",
    name="Positive Link Margin",
    metric_key="link_margin_db",
    op=">=",
    value=0.0,
    severity="must",
)

# Create requirement set
requirements = RequirementSet(
    requirements=[req1, req2],
    name="Communications Requirements",
)
```

### Verifying Requirements

```python
from phased_array_systems.evaluate import evaluate_case

metrics = evaluate_case(arch, scenario)
report = requirements.verify(metrics)

# Check overall status
print(f"Overall: {'PASS' if report.passes else 'FAIL'}")
print(f"Must: {report.must_pass_count}/{report.must_total_count}")

# Check individual requirements
for result in report.results:
    status = "PASS" if result.passes else "FAIL"
    print(f"{result.requirement.id}: {status} (margin: {result.margin:.1f})")
```

### Checking Individual Requirements

```python
req = Requirement("TEST", "Test", "value", ">=", 10.0)

# Check if value passes
print(req.check(15.0))  # True
print(req.check(5.0))   # False

# Compute margin
print(req.compute_margin(15.0))  # 5.0
print(req.compute_margin(5.0))   # -5.0
```

### Serializing Reports

```python
report = requirements.verify(metrics)
report_dict = report.to_dict()

# Contains structured verification data
import json
print(json.dumps(report_dict, indent=2))
```

## Type Aliases

```python
from phased_array_systems.types import ComparisonOp, Severity

# ComparisonOp = Literal[">=", "<=", ">", "<", "=="]
# Severity = Literal["must", "should", "nice"]
```

## See Also

- [User Guide: Requirements](../user-guide/requirements.md)
- [Architecture API](architecture.md)
- [Trades API](trades.md)
