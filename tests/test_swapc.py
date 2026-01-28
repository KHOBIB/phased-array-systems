"""Tests for SWaP-C models."""

import pytest

from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    CostConfig,
    RFChainConfig,
)
from phased_array_systems.models.swapc import CostModel, PowerModel
from phased_array_systems.models.swapc.cost import compute_cost_per_db, compute_cost_per_watt
from phased_array_systems.models.swapc.power import compute_thermal_load
from phased_array_systems.scenarios import CommsLinkScenario


class TestPowerModel:
    """Tests for the PowerModel."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8),  # 64 elements
            rf=RFChainConfig(
                tx_power_w_per_elem=1.0,  # 1W per element
                pa_efficiency=0.3,  # 30% efficiency
            ),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

    def test_model_creation(self):
        """Test model can be created."""
        model = PowerModel()
        assert model.name == "power"
        assert model.overhead_factor == 0.2

    def test_rf_power_calculation(self, sample_architecture, sample_scenario):
        """Test RF power calculation."""
        model = PowerModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # 64 elements * 1W = 64W
        assert metrics["rf_power_w"] == pytest.approx(64.0)

    def test_dc_power_calculation(self, sample_architecture, sample_scenario):
        """Test DC power calculation."""
        model = PowerModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # DC = RF / efficiency = 64 / 0.3 ≈ 213.3W
        expected_dc = 64.0 / 0.3
        assert metrics["dc_power_w"] == pytest.approx(expected_dc)

    def test_prime_power_calculation(self, sample_architecture, sample_scenario):
        """Test prime power with overhead."""
        model = PowerModel(overhead_factor=0.2)
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # Prime = DC * (1 + 0.2) = DC * 1.2
        expected_prime = (64.0 / 0.3) * 1.2
        assert metrics["prime_power_w"] == pytest.approx(expected_prime)

    def test_custom_overhead(self, sample_architecture, sample_scenario):
        """Test custom overhead factor."""
        model = PowerModel(overhead_factor=0.5)  # 50% overhead
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        expected_prime = (64.0 / 0.3) * 1.5
        assert metrics["prime_power_w"] == pytest.approx(expected_prime)


class TestThermalLoad:
    """Tests for thermal load calculation."""

    def test_basic_thermal(self):
        """Test basic thermal dissipation calculation."""
        result = compute_thermal_load(
            dc_power_w=200.0,
            rf_power_w=60.0,
        )

        # Heat = 200 - 60 = 140W
        assert result["heat_dissipation_w"] == pytest.approx(140.0)
        # Efficiency = 60/200 = 0.3
        assert result["rf_efficiency"] == pytest.approx(0.3)

    def test_with_additional_dissipation(self):
        """Test thermal with additional heat sources."""
        result = compute_thermal_load(
            dc_power_w=200.0,
            rf_power_w=60.0,
            additional_dissipation_w=20.0,
        )

        # Heat = 200 - 60 + 20 = 160W
        assert result["heat_dissipation_w"] == pytest.approx(160.0)


class TestCostModel:
    """Tests for the CostModel."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8),  # 64 elements
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
            cost=CostConfig(
                cost_per_elem_usd=100.0,
                nre_usd=10000.0,
                integration_cost_usd=5000.0,
            ),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

    def test_model_creation(self):
        """Test model can be created."""
        model = CostModel()
        assert model.name == "cost"

    def test_recurring_cost(self, sample_architecture, sample_scenario):
        """Test recurring cost calculation."""
        model = CostModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # 64 elements * $100 = $6,400
        assert metrics["recurring_cost_usd"] == pytest.approx(6400.0)

    def test_total_cost(self, sample_architecture, sample_scenario):
        """Test total cost calculation."""
        model = CostModel()
        metrics = model.evaluate(sample_architecture, sample_scenario, {})

        # Total = 6400 + 10000 + 5000 = $21,400
        assert metrics["total_cost_usd"] == pytest.approx(21400.0)
        assert metrics["cost_usd"] == pytest.approx(21400.0)

    def test_cost_scales_with_elements(self):
        """Test that cost scales with array size."""
        model = CostModel()
        scenario = CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

        arch_small = Architecture(
            array=ArrayConfig(nx=4, ny=4),  # 16 elements
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
            cost=CostConfig(cost_per_elem_usd=100.0),
        )

        arch_large = Architecture(
            array=ArrayConfig(nx=16, ny=16),  # 256 elements
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
            cost=CostConfig(cost_per_elem_usd=100.0),
        )

        metrics_small = model.evaluate(arch_small, scenario, {})
        metrics_large = model.evaluate(arch_large, scenario, {})

        # Large should be 16x more expensive in recurring cost
        assert metrics_large["recurring_cost_usd"] == 16 * metrics_small["recurring_cost_usd"]


class TestCostUtilities:
    """Tests for cost utility functions."""

    def test_cost_per_watt(self):
        """Test cost per Watt calculation."""
        cost_per_w = compute_cost_per_watt(10000.0, 100.0)
        assert cost_per_w == pytest.approx(100.0)  # $100/W

    def test_cost_per_watt_zero_power(self):
        """Test cost per Watt with zero power."""
        cost_per_w = compute_cost_per_watt(10000.0, 0.0)
        assert cost_per_w == float("inf")

    def test_cost_per_db(self):
        """Test cost per dBW calculation."""
        cost_per_db = compute_cost_per_db(10000.0, 40.0)
        assert cost_per_db == pytest.approx(250.0)  # $250/dBW
