# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`phased-array-systems` is an open-source Python package for phased array antenna system design, optimization, and performance visualization for wireless communications and radar applications. It implements an MBSE/MDAO workflow: requirements → architecture → analytical models → trade studies → Pareto selection → reporting.

**Core dependency:** `phased-array-modeling>=1.2.0` (provides array geometries, steering, tapering, impairments, and pattern visualization)

**Project status:** Design phase (no code implemented yet). See `package_design_and_requirements.txt` for the complete SDD.

## Build & Development Commands

```bash
# Installation (once implemented)
pip install phased-array-systems
pip install phased-array-systems[dev]       # Development deps (pytest, ruff, mypy)
pip install phased-array-systems[plotting]  # Visualization (plotly, kaleido)

# Testing
pytest tests/
pytest tests/test_comms_link_budget.py -v
pytest tests/ --cov=phased_array_systems

# Linting & Formatting
ruff check .
ruff format .
mypy src/phased_array_systems

# CLI (planned)
pasys run config.yaml      # Single case evaluation
pasys doe config.yaml      # DOE batch study
pasys pareto results.parquet --x cost_usd --y eirp_dbw
```

## Architecture

### Layer Structure
- **Layer 0:** `phased-array-modeling` (external) - EM/pattern computations
- **Layer 1:** This package - system models, trade studies, optimization
- **Layer 2:** Interfaces - Python API, CLI, config I/O

### Package Layout (`src/phased_array_systems/`)
- `requirements/` - Constraint/objective definitions, verification reports
- `architecture/` - ArrayConfig, RFChainConfig, PowerThermalConfig, CostConfig
- `models/antenna/` - Adapter wrapping `phased-array-modeling`, pattern metrics extraction
- `models/comms/` - Link budget (SNR, margin, EIRP), propagation models
- `models/radar/` - Radar equation, PD/PFA threshold helpers, integration gains
- `models/swapc/` - Power, thermal, and cost models
- `trades/` - DOE generation, batch runner, Pareto extraction, optimization
- `viz/` - Plots (Pareto, scatter-matrix), HTML/Markdown report generation
- `io/` - Config loading (YAML/JSON), results export (Parquet/CSV)
- `cli.py` - `pasys` command entrypoint

### Core Contracts

**ModelBlock Protocol:**
```python
class ModelBlock(Protocol):
    name: str
    def evaluate(self, arch: Architecture, scenario: Scenario, context: dict) -> dict:
        """Returns flat metrics dict"""
```

**Canonical Metrics Dictionary** (universal exchange format):
- Antenna: `g_peak_db`, `beamwidth_az_deg`, `beamwidth_el_deg`, `sll_db`, `scan_loss_db`
- Comms: `eirp_dbw`, `path_loss_db`, `snr_rx_db`, `link_margin_db`
- Radar: `snr_single_pulse_db`, `snr_required_db`, `snr_margin_db`, `pd`, `pfa`
- SWaP-C: `prime_power_w`, `weight_kg`, `cost_usd`
- Metadata: `meta.case_id`, `meta.runtime_s`, `meta.seed`, `meta.error`

### Data Flow
```
Config (YAML/JSON) → Pydantic validation → [Architecture + Scenario + RequirementSet]
    → DOE case generation → Batch evaluation (parallel, cached)
    → Requirement verification → Pareto extraction → Visualization/Reports
```

## Design Principles

1. **Requirements as first-class objects** - Every run produces pass/fail + margins with traceability
2. **Trade-space first** - DOE + Pareto over single-point designs; grey-out infeasible cases
3. **Flat metrics dictionary** - All models return consistent `dict[str, float]` for interchange
4. **Config-driven reproducibility** - Stable case IDs, seed control, version stamping
5. **Safe configs** - No `eval()`, data-driven configs only
6. **Case-level error handling** - DOE runs never crash for single-case failures

## Implementation Phases

1. **Phase 1 (MVP):** Schemas, config loader, requirements verification, antenna adapter, comms link budget
2. **Phase 2:** DOE generator, batch runner with resume, Pareto extraction, plots, Parquet export
3. **Phase 3:** Radar equation, detection threshold helpers, radar trade examples
4. **Phase 4:** CLI (`pasys`), HTML/Markdown report generation, PyPI publish

## Future Goals

**Interactive Web Application:** The package is designed to eventually power an interactive Streamlit or Vercel webapp for browser-based trade studies and visualization. Keep the core logic decoupled from CLI/reporting concerns to facilitate web integration.
