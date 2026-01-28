"""Tests for communications link budget model."""

import math

import pytest

from phased_array_systems.architecture import Architecture, ArrayConfig, RFChainConfig
from phased_array_systems.constants import K_B, C
from phased_array_systems.models.comms import CommsLinkModel, compute_fspl
from phased_array_systems.models.comms.link_budget import compute_link_margin
from phased_array_systems.scenarios import CommsLinkScenario


class TestPropagation:
    """Tests for propagation loss functions."""

    def test_fspl_known_value(self):
        """Test FSPL against known values."""
        # At 1 GHz and 1 km
        # FSPL = 20*log10(4*pi*1000*1e9/3e8)
        #      = 20*log10(4*pi*1000/0.3)
        #      ≈ 92.4 dB
        fspl = compute_fspl(1e9, 1000)
        expected = 20 * math.log10(4 * math.pi * 1000 / 0.3)
        assert fspl == pytest.approx(expected, rel=0.001)

    def test_fspl_frequency_scaling(self):
        """Test that FSPL increases by 6 dB when frequency doubles."""
        fspl_1ghz = compute_fspl(1e9, 1000)
        fspl_2ghz = compute_fspl(2e9, 1000)
        assert (fspl_2ghz - fspl_1ghz) == pytest.approx(6.02, rel=0.01)

    def test_fspl_range_scaling(self):
        """Test that FSPL increases by 6 dB when range doubles."""
        fspl_1km = compute_fspl(1e9, 1000)
        fspl_2km = compute_fspl(1e9, 2000)
        assert (fspl_2km - fspl_1km) == pytest.approx(6.02, rel=0.01)

    def test_fspl_invalid_inputs(self):
        """Test that invalid inputs raise ValueError."""
        with pytest.raises(ValueError):
            compute_fspl(-1e9, 1000)
        with pytest.raises(ValueError):
            compute_fspl(1e9, -1000)


class TestCommsLinkModel:
    """Tests for the CommsLinkModel."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8, dx_lambda=0.5, dy_lambda=0.5),
            rf=RFChainConfig(
                tx_power_w_per_elem=1.0,
                pa_efficiency=0.3,
                noise_figure_db=3.0,
                feed_loss_db=1.0,
            ),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,  # 10 GHz
            bandwidth_hz=10e6,  # 10 MHz
            range_m=100e3,  # 100 km
            required_snr_db=10.0,
            rx_antenna_gain_db=0.0,  # Isotropic RX
            rx_noise_temp_k=290.0,
        )

    def test_model_creation(self):
        """Test model can be created."""
        model = CommsLinkModel()
        assert model.name == "comms_link"

    def test_basic_evaluation(self, sample_architecture, sample_scenario):
        """Test basic link budget evaluation."""
        model = CommsLinkModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # Check all expected keys
        assert "tx_power_total_dbw" in metrics
        assert "eirp_dbw" in metrics
        assert "path_loss_db" in metrics
        assert "rx_power_dbw" in metrics
        assert "snr_rx_db" in metrics
        assert "link_margin_db" in metrics

    def test_tx_power_calculation(self, sample_architecture, sample_scenario):
        """Test transmit power calculation."""
        model = CommsLinkModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # 64 elements * 1W = 64W total
        expected_total_w = 64.0
        expected_total_dbw = 10 * math.log10(expected_total_w)
        assert metrics["tx_power_total_dbw"] == pytest.approx(expected_total_dbw)

    def test_eirp_calculation(self, sample_architecture, sample_scenario):
        """Test EIRP calculation."""
        model = CommsLinkModel()

        # Provide antenna gain in context
        context = {"g_peak_db": 25.0, "scan_loss_db": 0.0}
        metrics = model.evaluate(sample_architecture, sample_scenario, context)

        # EIRP = TX_power + Gain - TX_loss
        # TX_power = 10*log10(64) ≈ 18.06 dBW
        # Gain = 25 dB
        # TX_loss = 1 dB (feed) + 0 dB (system) = 1 dB
        # EIRP = 18.06 + 25 - 1 = 42.06 dBW
        expected_eirp = 10 * math.log10(64) + 25.0 - 1.0
        assert metrics["eirp_dbw"] == pytest.approx(expected_eirp, rel=0.01)

    def test_path_loss_calculation(self, sample_architecture, sample_scenario):
        """Test path loss calculation."""
        model = CommsLinkModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # Calculate expected FSPL at 10 GHz, 100 km
        wavelength = C / 10e9
        expected_fspl = 20 * math.log10(4 * math.pi * 100e3 / wavelength)
        assert metrics["fspl_db"] == pytest.approx(expected_fspl, rel=0.001)

    def test_noise_power_calculation(self, sample_architecture, sample_scenario):
        """Test noise power calculation."""
        model = CommsLinkModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # N = k*T*B
        # k = 1.38e-23 J/K
        # T = 290 K
        # B = 10 MHz
        noise_w = K_B * 290 * 10e6
        noise_dbw = 10 * math.log10(noise_w) + 3.0  # +3 dB noise figure
        assert metrics["noise_power_dbw"] == pytest.approx(noise_dbw, rel=0.01)

    def test_link_margin_positive(self, sample_architecture):
        """Test that a well-designed link has positive margin."""
        model = CommsLinkModel()

        # Short range, high bandwidth link
        scenario = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=1e6,  # 1 MHz (less noise)
            range_m=10e3,  # 10 km (less path loss)
            required_snr_db=10.0,
            rx_antenna_gain_db=10.0,  # Directive RX antenna
        )

        context = {"g_peak_db": 25.0}
        metrics = model.evaluate(sample_architecture, scenario, context)

        # Should have positive margin for this favorable scenario
        assert metrics["link_margin_db"] > 0

    def test_link_margin_with_extra_losses(self, sample_architecture):
        """Test that extra losses reduce link margin."""
        model = CommsLinkModel()

        scenario_no_loss = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

        scenario_with_loss = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
            atmospheric_loss_db=2.0,
            rain_loss_db=3.0,
        )

        context = {"g_peak_db": 25.0}
        metrics_no_loss = model.evaluate(sample_architecture, scenario_no_loss, context)
        metrics_with_loss = model.evaluate(sample_architecture, scenario_with_loss, context)

        # Margin should decrease by 5 dB (2 + 3)
        margin_diff = metrics_no_loss["link_margin_db"] - metrics_with_loss["link_margin_db"]
        assert margin_diff == pytest.approx(5.0, rel=0.01)


class TestComputeLinkMargin:
    """Tests for the standalone link margin function."""

    def test_basic_calculation(self):
        """Test basic link margin calculation."""
        result = compute_link_margin(
            eirp_dbw=40.0,
            path_loss_db=150.0,
            g_rx_db=10.0,
            noise_temp_k=290.0,
            bandwidth_hz=1e6,
            noise_figure_db=3.0,
            required_snr_db=10.0,
        )

        # rx_power = 40 - 150 + 10 = -100 dBW
        assert result["rx_power_dbw"] == pytest.approx(-100.0)

        # SNR and margin should be computed
        assert "snr_db" in result
        assert "margin_db" in result
