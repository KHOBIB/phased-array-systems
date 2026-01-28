"""Tests for the antenna adapter and metrics."""

import math

import numpy as np
import pytest

from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig
from phased_array_systems.models.antenna import (
    PhasedArrayAdapter,
    compute_beamwidth,
    compute_scan_loss,
    compute_sidelobe_level,
)
from phased_array_systems.models.antenna.metrics import (
    compute_array_gain,
    compute_directivity_rectangular,
)
from phased_array_systems.scenarios import CommsLinkScenario


class TestMetricFunctions:
    """Tests for metric extraction functions."""

    def test_compute_beamwidth_sinc(self):
        """Test beamwidth computation with a sinc-like pattern."""
        angles = np.linspace(-30, 30, 601)
        # Create a sinc-like pattern with normalized sinc
        # For sinc(x), the -3dB points are at x ≈ ±0.443
        # With angles in degrees and x = angles/scale, bw ≈ 0.886*scale degrees
        scale = 2.0  # degrees per unit x
        x = angles / scale
        pattern = np.sinc(x)  # sinc(x) = sin(pi*x)/(pi*x)
        pattern_db = 20 * np.log10(np.abs(pattern) + 1e-12)

        bw = compute_beamwidth(pattern_db, angles, -3.0)
        # Actual -3dB width of sinc is approximately 0.886 * 2 * scale = 1.77 degrees
        assert 1.0 < bw < 3.0

    def test_compute_sidelobe_level(self):
        """Test sidelobe level computation."""
        angles = np.linspace(-60, 60, 1201)
        x = np.radians(angles) * 10
        pattern = np.sinc(x / np.pi)
        pattern_db = 20 * np.log10(np.abs(pattern) + 1e-12)

        sll = compute_sidelobe_level(pattern_db, angles)
        # Sinc first sidelobe is about -13.2 dB
        assert -15.0 < sll < -12.0

    def test_compute_scan_loss_boresight(self):
        """Test scan loss at boresight (should be 0)."""
        loss = compute_scan_loss(0.0)
        assert loss == pytest.approx(0.0)

    def test_compute_scan_loss_45deg(self):
        """Test scan loss at 45 degrees."""
        loss = compute_scan_loss(45.0)
        # cos(45) = 0.707, 10*log10(0.707) ≈ -1.5 dB
        expected = -10 * math.log10(math.cos(math.radians(45)))
        assert loss == pytest.approx(expected, rel=0.01)

    def test_compute_scan_loss_60deg(self):
        """Test scan loss at 60 degrees."""
        loss = compute_scan_loss(60.0)
        # cos(60) = 0.5, 10*log10(0.5) ≈ -3 dB
        expected = -10 * math.log10(0.5)
        assert loss == pytest.approx(expected, rel=0.01)

    def test_compute_array_gain(self):
        """Test array gain computation."""
        # 64 elements with 0 dB element gain
        gain = compute_array_gain(64, 0.0)
        expected = 10 * math.log10(64)  # ~18.06 dB
        assert gain == pytest.approx(expected)

        # With element gain
        gain_with_elem = compute_array_gain(64, 5.0)
        assert gain_with_elem == pytest.approx(expected + 5.0)

    def test_compute_directivity_rectangular(self):
        """Test directivity computation for rectangular array."""
        # 8x8 array with half-wavelength spacing
        directivity = compute_directivity_rectangular(8, 8, 0.5, 0.5)
        # D ≈ 4*pi * (8*0.5) * (8*0.5) = 4*pi*16 = 201 ≈ 23 dB
        expected = 10 * math.log10(4 * math.pi * 16)
        assert directivity == pytest.approx(expected, rel=0.01)


class TestPhasedArrayAdapter:
    """Tests for the PhasedArrayAdapter class."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,  # 10 GHz
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
            scan_angle_deg=0.0,
        )

    def test_adapter_creation(self):
        """Test adapter can be created."""
        adapter = PhasedArrayAdapter(use_analytical_fallback=True)
        assert adapter.name == "antenna"

    def test_evaluate_boresight(self, sample_architecture, sample_scenario):
        """Test evaluation at boresight."""
        adapter = PhasedArrayAdapter(use_analytical_fallback=True)
        metrics = adapter.evaluate(sample_architecture, sample_scenario, {})

        assert "g_peak_db" in metrics
        assert "beamwidth_az_deg" in metrics
        assert "beamwidth_el_deg" in metrics
        assert "sll_db" in metrics
        assert "scan_loss_db" in metrics
        assert "n_elements" in metrics

        # Sanity checks
        assert metrics["g_peak_db"] > 20  # Should be significant gain
        assert metrics["scan_loss_db"] == pytest.approx(0.0)  # No scan loss at boresight
        assert metrics["n_elements"] == 64
        assert 0 < metrics["beamwidth_az_deg"] < 20
        assert 0 < metrics["beamwidth_el_deg"] < 20

    def test_evaluate_with_scan(self, sample_architecture):
        """Test evaluation with scan angle."""
        adapter = PhasedArrayAdapter(use_analytical_fallback=True)

        scenario = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
            scan_angle_deg=45.0,
        )

        metrics = adapter.evaluate(sample_architecture, scenario, {})

        # Should have scan loss at 45 degrees
        assert metrics["scan_loss_db"] > 1.0
        # Peak gain should be reduced by scan loss
        assert metrics["g_peak_db"] < metrics["directivity_db"]

    def test_evaluate_different_array_sizes(self):
        """Test that larger arrays have higher gain."""
        adapter = PhasedArrayAdapter(use_analytical_fallback=True)

        scenario = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

        arch_small = Architecture(
            array=ArrayConfig(nx=4, ny=4),
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
        )
        arch_large = Architecture(
            array=ArrayConfig(nx=16, ny=16),
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
        )

        metrics_small = adapter.evaluate(arch_small, scenario, {})
        metrics_large = adapter.evaluate(arch_large, scenario, {})

        # Larger array should have higher gain
        assert metrics_large["g_peak_db"] > metrics_small["g_peak_db"]
        # Larger array should have narrower beamwidth
        assert metrics_large["beamwidth_az_deg"] < metrics_small["beamwidth_az_deg"]
