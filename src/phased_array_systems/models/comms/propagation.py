"""Propagation loss models for communications links."""

import math

from phased_array_systems.constants import C


def compute_fspl(freq_hz: float, range_m: float) -> float:
    """Compute Free Space Path Loss (FSPL).

    FSPL = 20*log10(4*pi*d*f/c)
         = 20*log10(d) + 20*log10(f) + 20*log10(4*pi/c)
         = 20*log10(d) + 20*log10(f) - 147.55 (with d in m, f in Hz)

    Args:
        freq_hz: Frequency in Hz
        range_m: Range/distance in meters

    Returns:
        Free space path loss in dB (positive value)
    """
    if freq_hz <= 0:
        raise ValueError("Frequency must be positive")
    if range_m <= 0:
        raise ValueError("Range must be positive")

    wavelength = C / freq_hz
    fspl_linear = (4 * math.pi * range_m / wavelength) ** 2
    return 10 * math.log10(fspl_linear)


def compute_fspl_wavelength(wavelength_m: float, range_m: float) -> float:
    """Compute FSPL given wavelength directly.

    Args:
        wavelength_m: Wavelength in meters
        range_m: Range/distance in meters

    Returns:
        Free space path loss in dB (positive value)
    """
    if wavelength_m <= 0:
        raise ValueError("Wavelength must be positive")
    if range_m <= 0:
        raise ValueError("Range must be positive")

    fspl_linear = (4 * math.pi * range_m / wavelength_m) ** 2
    return 10 * math.log10(fspl_linear)


def compute_two_ray_path_loss(
    freq_hz: float,
    range_m: float,
    h_tx_m: float,
    h_rx_m: float,
) -> float:
    """Compute two-ray ground reflection path loss.

    At short ranges, behaves like FSPL. At long ranges (beyond crossover
    distance), follows d^4 attenuation.

    Args:
        freq_hz: Frequency in Hz
        range_m: Horizontal range in meters
        h_tx_m: Transmitter height in meters
        h_rx_m: Receiver height in meters

    Returns:
        Path loss in dB (positive value)
    """
    wavelength = C / freq_hz

    # Crossover distance
    d_cross = 4 * h_tx_m * h_rx_m / wavelength

    if range_m < d_cross:
        # Use FSPL in near region
        return compute_fspl(freq_hz, range_m)
    else:
        # Two-ray model: PL = 40*log10(d) - 20*log10(ht*hr)
        # Normalized to match FSPL at crossover
        pl_cross = compute_fspl(freq_hz, d_cross)
        pl_two_ray = pl_cross + 40 * math.log10(range_m / d_cross)
        return pl_two_ray
