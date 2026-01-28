"""Adapter wrapping phased-array-modeling for consistent metric extraction."""

from typing import Any

import numpy as np

from phased_array_systems.architecture import Architecture
from phased_array_systems.models.antenna.metrics import (
    compute_beamwidth,
    compute_directivity_rectangular,
    compute_scan_loss,
    compute_sidelobe_level,
)
from phased_array_systems.types import MetricsDict, Scenario

# Try to import phased-array-modeling, fall back to stub if not available
try:
    from phased_array_modeling import (
        RectangularArray,
        compute_array_factor,
    )

    HAS_PAM = True
except ImportError:
    HAS_PAM = False


class PhasedArrayAdapter:
    """Adapter for phased-array-modeling library.

    Provides a consistent interface for computing antenna pattern metrics
    using the phased-array-modeling library, with fallback to analytical
    approximations when the library is not available.

    Attributes:
        name: Model block name for identification
        use_analytical_fallback: If True, use analytical approximations
            when phased-array-modeling is not available
    """

    name: str = "antenna"

    def __init__(self, use_analytical_fallback: bool = True):
        """Initialize the adapter.

        Args:
            use_analytical_fallback: Use analytical methods if PAM unavailable
        """
        self.use_analytical_fallback = use_analytical_fallback

        if not HAS_PAM and not use_analytical_fallback:
            raise ImportError(
                "phased-array-modeling not installed. Install with: "
                "pip install phased-array-modeling"
            )

    def evaluate(
        self, arch: Architecture, scenario: Scenario, context: dict[str, Any]
    ) -> MetricsDict:
        """Evaluate antenna performance metrics.

        Args:
            arch: Architecture configuration
            scenario: Scenario with frequency and scan angle info
            context: Additional context (unused)

        Returns:
            Dictionary with antenna metrics:
                - g_peak_db: Peak array gain (dB)
                - beamwidth_az_deg: Azimuth beamwidth (degrees)
                - beamwidth_el_deg: Elevation beamwidth (degrees)
                - sll_db: Peak sidelobe level (dB, negative)
                - scan_loss_db: Scan loss at operating angle (dB)
                - directivity_db: Array directivity (dB)
                - n_elements: Number of array elements
        """
        # Extract scan angle from scenario if available
        scan_angle_deg = getattr(scenario, "scan_angle_deg", 0.0)

        if HAS_PAM:
            return self._evaluate_with_pam(arch, scenario, scan_angle_deg)
        else:
            return self._evaluate_analytical(arch, scenario, scan_angle_deg)

    def _evaluate_with_pam(
        self, arch: Architecture, scenario: Scenario, scan_angle_deg: float
    ) -> MetricsDict:
        """Evaluate using phased-array-modeling library."""
        wavelength_m = scenario.wavelength_m if hasattr(scenario, "wavelength_m") else None

        if wavelength_m is None:
            from phased_array_systems.constants import C
            wavelength_m = C / scenario.freq_hz

        # Create array object
        array = RectangularArray(
            nx=arch.array.nx,
            ny=arch.array.ny,
            dx=arch.array.dx_lambda * wavelength_m,
            dy=arch.array.dy_lambda * wavelength_m,
        )

        # Compute array factor over theta range
        theta_deg = np.linspace(-90, 90, 361)
        theta_rad = np.radians(theta_deg)

        # Compute AF at phi=0 (azimuth cut)
        af_az = compute_array_factor(
            array,
            theta_rad,
            phi=0,
            wavelength=wavelength_m,
            scan_theta=np.radians(scan_angle_deg),
            scan_phi=0,
        )
        af_az_db = 20 * np.log10(np.abs(af_az) + 1e-12)
        af_az_db = af_az_db - np.max(af_az_db)  # Normalize to peak

        # Compute AF at phi=90 (elevation cut)
        af_el = compute_array_factor(
            array,
            theta_rad,
            phi=np.pi / 2,
            wavelength=wavelength_m,
            scan_theta=np.radians(scan_angle_deg),
            scan_phi=0,
        )
        af_el_db = 20 * np.log10(np.abs(af_el) + 1e-12)
        af_el_db = af_el_db - np.max(af_el_db)

        # Extract metrics
        beamwidth_az = compute_beamwidth(af_az_db, theta_deg)
        beamwidth_el = compute_beamwidth(af_el_db, theta_deg)
        sll = compute_sidelobe_level(af_az_db, theta_deg)
        scan_loss = compute_scan_loss(scan_angle_deg)
        directivity = compute_directivity_rectangular(
            arch.array.nx, arch.array.ny, arch.array.dx_lambda, arch.array.dy_lambda
        )
        g_peak = directivity - scan_loss  # Account for scan loss

        return {
            "g_peak_db": g_peak,
            "beamwidth_az_deg": beamwidth_az,
            "beamwidth_el_deg": beamwidth_el,
            "sll_db": sll,
            "scan_loss_db": scan_loss,
            "directivity_db": directivity,
            "n_elements": arch.array.n_elements,
        }

    def _evaluate_analytical(
        self, arch: Architecture, scenario: Scenario, scan_angle_deg: float
    ) -> MetricsDict:
        """Evaluate using analytical approximations.

        Uses standard phased array formulas when the full simulation
        library is not available.
        """
        # Directivity from aperture size
        directivity_db = compute_directivity_rectangular(
            arch.array.nx, arch.array.ny, arch.array.dx_lambda, arch.array.dy_lambda
        )

        # Scan loss
        scan_loss = compute_scan_loss(scan_angle_deg)

        # Peak gain (accounting for scan)
        g_peak = directivity_db - scan_loss

        # Beamwidth approximations for uniform rectangular array
        # BW ≈ 0.886 * lambda / (N * d) in radians, for uniform taper
        # With d in wavelengths: BW ≈ 0.886 / (N * d_lambda) radians
        bw_az_rad = 0.886 / (arch.array.nx * arch.array.dx_lambda)
        bw_el_rad = 0.886 / (arch.array.ny * arch.array.dy_lambda)

        beamwidth_az_deg = np.degrees(bw_az_rad)
        beamwidth_el_deg = np.degrees(bw_el_rad)

        # Sidelobe level for uniform taper (theoretical: -13.2 dB)
        sll_db = -13.2

        return {
            "g_peak_db": g_peak,
            "beamwidth_az_deg": beamwidth_az_deg,
            "beamwidth_el_deg": beamwidth_el_deg,
            "sll_db": sll_db,
            "scan_loss_db": scan_loss,
            "directivity_db": directivity_db,
            "n_elements": arch.array.n_elements,
        }
