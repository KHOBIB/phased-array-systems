"""Power consumption models for phased array systems."""

from typing import Any

from phased_array_systems.architecture import Architecture
from phased_array_systems.types import MetricsDict, Scenario


class PowerModel:
    """Power consumption calculator for phased array systems.

    Computes DC power, RF power, and prime power based on
    architecture parameters and efficiency factors.

    Power Equations:
        RF_power = n_elements * tx_power_per_elem
        DC_power = RF_power / pa_efficiency
        Prime_power = DC_power * (1 + overhead_factor)

    Attributes:
        name: Model block name for identification
        overhead_factor: Additional power overhead (cooling, control, etc.)
    """

    name: str = "power"

    def __init__(self, overhead_factor: float = 0.2):
        """Initialize power model.

        Args:
            overhead_factor: Fraction of DC power for overhead (default 20%)
        """
        self.overhead_factor = overhead_factor

    def evaluate(
        self,
        arch: Architecture,
        scenario: Scenario,
        context: dict[str, Any],
    ) -> MetricsDict:
        """Evaluate power metrics.

        Args:
            arch: Architecture configuration
            scenario: Scenario (may influence duty cycle)
            context: Additional context (unused)

        Returns:
            Dictionary with power metrics:
                - rf_power_w: Total RF output power (W)
                - dc_power_w: DC power consumption (W)
                - prime_power_w: Prime/wall power (W)
                - pa_efficiency: Power amplifier efficiency
                - n_elements: Number of array elements
        """
        n_elements = arch.array.n_elements
        tx_power_per_elem = arch.rf.tx_power_w_per_elem
        pa_efficiency = arch.rf.pa_efficiency

        # RF power
        rf_power_w = n_elements * tx_power_per_elem

        # DC power (accounting for PA efficiency)
        dc_power_w = rf_power_w / pa_efficiency

        # Prime power (including overhead)
        prime_power_w = dc_power_w * (1 + self.overhead_factor)

        return {
            "rf_power_w": rf_power_w,
            "dc_power_w": dc_power_w,
            "prime_power_w": prime_power_w,
            "pa_efficiency": pa_efficiency,
            "n_elements": n_elements,
        }


def compute_thermal_load(
    dc_power_w: float,
    rf_power_w: float,
    additional_dissipation_w: float = 0.0,
) -> dict[str, float]:
    """Compute thermal dissipation for heat management.

    Args:
        dc_power_w: Total DC power consumption (W)
        rf_power_w: RF power radiated (W)
        additional_dissipation_w: Other heat sources (W)

    Returns:
        Dictionary with thermal metrics:
            - heat_dissipation_w: Total heat to remove (W)
            - rf_efficiency: Fraction of DC converted to RF
    """
    # Heat = DC input - RF output + additional sources
    heat_dissipation_w = dc_power_w - rf_power_w + additional_dissipation_w
    rf_efficiency = rf_power_w / dc_power_w if dc_power_w > 0 else 0.0

    return {
        "heat_dissipation_w": heat_dissipation_w,
        "rf_efficiency": rf_efficiency,
    }
