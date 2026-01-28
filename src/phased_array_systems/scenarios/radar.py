"""Radar detection scenario definition (stub for Phase 3)."""

from typing import Literal

from pydantic import Field

from phased_array_systems.scenarios.base import ScenarioBase


class RadarDetectionScenario(ScenarioBase):
    """Scenario for radar detection analysis.

    Note: Full implementation planned for Phase 3.

    Attributes:
        freq_hz: Operating frequency (Hz)
        bandwidth_hz: Signal bandwidth (Hz)
        range_m: Target range (meters)
        target_rcs_dbsm: Target radar cross section (dBsm)
        pfa: Probability of false alarm
        pd_required: Required probability of detection
        n_pulses: Number of pulses integrated
        scan_angle_deg: Beam scan angle from boresight (degrees)
        integration_type: Coherent or non-coherent integration
    """

    bandwidth_hz: float = Field(gt=0, description="Signal bandwidth (Hz)")
    range_m: float = Field(gt=0, description="Target range (m)")
    target_rcs_dbsm: float = Field(description="Target RCS (dBsm)")
    pfa: float = Field(
        default=1e-6, gt=0, lt=1, description="Probability of false alarm"
    )
    pd_required: float = Field(
        default=0.9, gt=0, lt=1, description="Required probability of detection"
    )
    n_pulses: int = Field(default=1, ge=1, description="Number of pulses integrated")
    scan_angle_deg: float = Field(
        default=0.0, ge=0, le=90, description="Scan angle from boresight (deg)"
    )
    integration_type: Literal["coherent", "noncoherent"] = Field(
        default="noncoherent", description="Integration type"
    )
