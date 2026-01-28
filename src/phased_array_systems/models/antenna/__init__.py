"""Antenna modeling adapter wrapping phased-array-modeling."""

from phased_array_systems.models.antenna.adapter import PhasedArrayAdapter
from phased_array_systems.models.antenna.metrics import (
    compute_beamwidth,
    compute_scan_loss,
    compute_sidelobe_level,
)

__all__ = [
    "PhasedArrayAdapter",
    "compute_beamwidth",
    "compute_scan_loss",
    "compute_sidelobe_level",
]
