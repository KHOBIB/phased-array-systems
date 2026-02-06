"""Surface and volume clutter models for radar.

Implements empirical clutter RCS models for:
- Sea surface clutter (GIT model)
- Ground/terrain clutter (Nathanson model)
- Rain volume clutter

References:
    - Skolnik, M. "Radar Handbook", 3rd Ed., Ch. 7
    - Nathanson, F. "Radar Design Principles", 2nd Ed.
    - Long, M. "Radar Reflectivity of Land and Sea", 3rd Ed.
"""

from __future__ import annotations

import math
from typing import Literal

from phased_array_systems.constants import C_LIGHT

# Sea state parameters (Douglas scale approximation)
# Maps sea state (0-6) to approximate significant wave height (m)
SEA_STATE_TO_WAVE_HEIGHT = {
    0: 0.0,  # Calm (glassy)
    1: 0.1,  # Calm (rippled)
    2: 0.3,  # Smooth
    3: 0.9,  # Slight
    4: 1.5,  # Moderate
    5: 2.5,  # Rough
    6: 4.0,  # Very rough
}

TerrainType = Literal["rural", "urban", "forest", "desert", "wetland"]


def sea_clutter_sigma0(
    sea_state: int,
    grazing_angle_deg: float,
    freq_hz: float,
    polarization: Literal["HH", "VV", "HV"] = "HH",
) -> float:
    """Compute sea surface normalized radar cross section (sigma-0).

    Uses the GIT (Georgia Institute of Technology) model for sea
    clutter backscatter. Valid for frequencies 1-100 GHz.

    The GIT model provides sigma-0 in dB as a function of:
    - Grazing angle
    - Sea state (wave height)
    - Frequency
    - Polarization

    Args:
        sea_state: Sea state (0-6, Douglas scale)
        grazing_angle_deg: Grazing angle from horizon (deg), 0.1 to 90
        freq_hz: Radar frequency (Hz)
        polarization: Antenna polarization (HH, VV, or HV)

    Returns:
        Normalized RCS (sigma-0) in dB (dBsm/m^2)

    Raises:
        ValueError: If sea_state not in 0-6 or grazing angle invalid
    """
    if not 0 <= sea_state <= 6:
        raise ValueError("sea_state must be between 0 and 6")
    if not 0.1 <= grazing_angle_deg <= 90:
        raise ValueError("grazing_angle_deg must be between 0.1 and 90")

    # Convert to radians
    psi = math.radians(grazing_angle_deg)

    # Frequency in GHz
    freq_ghz = freq_hz / 1e9

    # Wave height factor
    h = SEA_STATE_TO_WAVE_HEIGHT.get(sea_state, 0.9)

    # GIT model coefficients (simplified empirical fit)
    # sigma_0 = A * sin(psi)^B * f^C * h^D
    # Coefficients vary by polarization

    if polarization == "HH":
        # Horizontal polarization - typically lower at low grazing
        a0 = -27.0
        b_psi = 1.0
        c_freq = 0.6
        d_wave = 0.9
    elif polarization == "VV":
        # Vertical polarization - less grazing angle dependence
        a0 = -23.0
        b_psi = 0.7
        c_freq = 0.5
        d_wave = 0.8
    else:  # HV cross-pol
        # Cross-polarization - typically 10-15 dB lower
        a0 = -40.0
        b_psi = 0.8
        c_freq = 0.5
        d_wave = 0.7

    # Compute sigma-0 in dB
    # Clamp frequency to valid range
    freq_ghz = max(1.0, min(100.0, freq_ghz))

    sigma0_db = (
        a0
        + b_psi * 10 * math.log10(math.sin(psi))
        + c_freq * 10 * math.log10(freq_ghz)
        + d_wave * 10 * math.log10(max(0.1, h))
    )

    return sigma0_db


def sea_clutter_rcs(
    sea_state: int,
    grazing_angle_deg: float,
    freq_hz: float,
    resolution_cell_m2: float,
    polarization: Literal["HH", "VV", "HV"] = "HH",
) -> float:
    """Compute sea surface clutter RCS for a resolution cell.

    Args:
        sea_state: Sea state (0-6, Douglas scale)
        grazing_angle_deg: Grazing angle from horizon (deg)
        freq_hz: Radar frequency (Hz)
        resolution_cell_m2: Resolution cell area (m^2)
        polarization: Antenna polarization

    Returns:
        Clutter RCS in dBsm
    """
    sigma0_db = sea_clutter_sigma0(sea_state, grazing_angle_deg, freq_hz, polarization)

    # Clutter RCS = sigma_0 * cell_area
    cell_area_db = 10 * math.log10(max(1.0, resolution_cell_m2))
    clutter_rcs_dbsm = sigma0_db + cell_area_db

    return clutter_rcs_dbsm


def ground_clutter_sigma0(
    terrain_type: TerrainType,
    grazing_angle_deg: float,
    freq_hz: float,
) -> float:
    """Compute ground surface normalized RCS (sigma-0).

    Uses Nathanson's empirical model for terrain clutter.
    Valid for frequencies 1-100 GHz.

    Args:
        terrain_type: Type of terrain surface
        grazing_angle_deg: Grazing angle from horizon (deg), 0.1 to 90
        freq_hz: Radar frequency (Hz)

    Returns:
        Normalized RCS (sigma-0) in dB (dBsm/m^2)

    Raises:
        ValueError: If grazing angle invalid
    """
    if not 0.1 <= grazing_angle_deg <= 90:
        raise ValueError("grazing_angle_deg must be between 0.1 and 90")

    psi = math.radians(grazing_angle_deg)
    freq_ghz = freq_hz / 1e9
    freq_ghz = max(1.0, min(100.0, freq_ghz))

    # Terrain-dependent coefficients (empirical, from Nathanson)
    # sigma_0 ≈ gamma_0 * sin(psi)^n where gamma_0 is a constant
    terrain_params = {
        "rural": {"gamma0_db": -20.0, "n": 0.8, "freq_exp": 0.3},
        "urban": {"gamma0_db": -10.0, "n": 0.5, "freq_exp": 0.4},
        "forest": {"gamma0_db": -15.0, "n": 0.6, "freq_exp": 0.5},
        "desert": {"gamma0_db": -30.0, "n": 1.0, "freq_exp": 0.2},
        "wetland": {"gamma0_db": -18.0, "n": 0.7, "freq_exp": 0.4},
    }

    params = terrain_params.get(terrain_type, terrain_params["rural"])

    sigma0_db = (
        params["gamma0_db"]
        + params["n"] * 10 * math.log10(math.sin(psi))
        + params["freq_exp"] * 10 * math.log10(freq_ghz)
    )

    return sigma0_db


def ground_clutter_rcs(
    terrain_type: TerrainType,
    grazing_angle_deg: float,
    freq_hz: float,
    resolution_cell_m2: float,
) -> float:
    """Compute ground clutter RCS for a resolution cell.

    Args:
        terrain_type: Type of terrain surface
        grazing_angle_deg: Grazing angle from horizon (deg)
        freq_hz: Radar frequency (Hz)
        resolution_cell_m2: Resolution cell area (m^2)

    Returns:
        Clutter RCS in dBsm
    """
    sigma0_db = ground_clutter_sigma0(terrain_type, grazing_angle_deg, freq_hz)

    cell_area_db = 10 * math.log10(max(1.0, resolution_cell_m2))
    clutter_rcs_dbsm = sigma0_db + cell_area_db

    return clutter_rcs_dbsm


def rain_reflectivity(
    rain_rate_mm_hr: float,
    freq_hz: float,
) -> float:
    """Compute rain volume reflectivity (eta) in dB.

    Uses the Z-R relationship and Rayleigh scattering.
    Z = 200 * R^1.6 (Marshall-Palmer relation)

    Args:
        rain_rate_mm_hr: Rain rate (mm/hour)
        freq_hz: Radar frequency (Hz)

    Returns:
        Volume reflectivity (eta) in dB (dBsm/m^3)
    """
    if rain_rate_mm_hr <= 0:
        return -100.0  # Essentially no rain clutter

    # Marshall-Palmer Z-R relationship
    # Z (mm^6/m^3) = 200 * R^1.6
    z = 200 * (rain_rate_mm_hr**1.6)

    # Convert Z to reflectivity factor
    wavelength_m = C_LIGHT / freq_hz
    wavelength_cm = wavelength_m * 100

    # Rayleigh scattering: eta = (pi^5 / lambda^4) * |K|^2 * Z
    # |K|^2 ≈ 0.93 for water at microwave frequencies
    k_squared = 0.93

    # eta in m^-1 (linear)
    eta_linear = (
        (math.pi**5) / (wavelength_cm**4) * k_squared * z * 1e-18  # Convert mm^6 to m^6
    )

    # Convert to dB (dBsm/m^3)
    eta_db = 10 * math.log10(max(1e-20, eta_linear))

    return eta_db


def rain_clutter_rcs(
    rain_rate_mm_hr: float,
    freq_hz: float,
    resolution_volume_m3: float,
) -> float:
    """Compute rain volume clutter RCS.

    Args:
        rain_rate_mm_hr: Rain rate (mm/hour)
        freq_hz: Radar frequency (Hz)
        resolution_volume_m3: Resolution cell volume (m^3)

    Returns:
        Rain clutter RCS in dBsm
    """
    eta_db = rain_reflectivity(rain_rate_mm_hr, freq_hz)

    volume_db = 10 * math.log10(max(1.0, resolution_volume_m3))
    clutter_rcs_dbsm = eta_db + volume_db

    return clutter_rcs_dbsm


def compute_resolution_cell_area(
    range_m: float,
    range_resolution_m: float,
    azimuth_beamwidth_deg: float,
) -> float:
    """Compute resolution cell area for surface clutter.

    Area = range_resolution * range * azimuth_beamwidth (in radians)

    Args:
        range_m: Range to cell center (m)
        range_resolution_m: Range resolution (m), typically c/(2*B)
        azimuth_beamwidth_deg: Azimuth beamwidth (deg)

    Returns:
        Resolution cell area (m^2)
    """
    azimuth_rad = math.radians(azimuth_beamwidth_deg)
    cross_range_m = range_m * azimuth_rad
    area_m2 = range_resolution_m * cross_range_m
    return area_m2


def compute_resolution_volume(
    range_m: float,
    range_resolution_m: float,
    azimuth_beamwidth_deg: float,
    elevation_beamwidth_deg: float,
) -> float:
    """Compute resolution cell volume for volume clutter.

    Volume = range_resolution * (range * az_bw) * (range * el_bw)

    Args:
        range_m: Range to cell center (m)
        range_resolution_m: Range resolution (m)
        azimuth_beamwidth_deg: Azimuth beamwidth (deg)
        elevation_beamwidth_deg: Elevation beamwidth (deg)

    Returns:
        Resolution cell volume (m^3)
    """
    az_rad = math.radians(azimuth_beamwidth_deg)
    el_rad = math.radians(elevation_beamwidth_deg)

    cross_range_az = range_m * az_rad
    cross_range_el = range_m * el_rad

    volume_m3 = range_resolution_m * cross_range_az * cross_range_el
    return volume_m3


def compute_scr(
    target_rcs_dbsm: float,
    clutter_rcs_dbsm: float,
) -> float:
    """Compute signal-to-clutter ratio.

    Args:
        target_rcs_dbsm: Target RCS (dBsm)
        clutter_rcs_dbsm: Clutter RCS (dBsm)

    Returns:
        Signal-to-clutter ratio (dB)
    """
    return target_rcs_dbsm - clutter_rcs_dbsm


def compute_scnr(
    snr_db: float,
    scr_db: float,
) -> float:
    """Compute signal-to-clutter-plus-noise ratio.

    SCNR = 1 / (1/SNR + 1/SCR)

    In dB form, this requires conversion to linear.

    Args:
        snr_db: Signal-to-noise ratio (dB)
        scr_db: Signal-to-clutter ratio (dB)

    Returns:
        Signal-to-clutter-plus-noise ratio (dB)
    """
    snr_linear = 10 ** (snr_db / 10)
    scr_linear = 10 ** (scr_db / 10)

    # SCNR = S / (C + N) = 1 / (1/SNR + 1/SCR)
    if snr_linear <= 0 or scr_linear <= 0:
        return min(snr_db, scr_db)

    scnr_linear = 1.0 / (1.0 / snr_linear + 1.0 / scr_linear)
    scnr_db = 10 * math.log10(scnr_linear)

    return scnr_db
