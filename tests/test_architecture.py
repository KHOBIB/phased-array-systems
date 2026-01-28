"""Tests for the architecture configuration subsystem."""

import pytest
from pydantic import ValidationError

from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    CostConfig,
    RFChainConfig,
)


class TestArrayConfig:
    """Tests for ArrayConfig."""

    def test_default_values(self):
        config = ArrayConfig(nx=8, ny=8)
        assert config.geometry == "rectangular"
        assert config.dx_lambda == 0.5
        assert config.dy_lambda == 0.5
        assert config.scan_limit_deg == 60.0

    def test_n_elements(self):
        config = ArrayConfig(nx=8, ny=16)
        assert config.n_elements == 128

    def test_invalid_nx(self):
        with pytest.raises(ValidationError):
            ArrayConfig(nx=0, ny=8)

    def test_invalid_spacing(self):
        with pytest.raises(ValidationError):
            ArrayConfig(nx=8, ny=8, dx_lambda=-0.5)

    def test_invalid_scan_limit(self):
        with pytest.raises(ValidationError):
            ArrayConfig(nx=8, ny=8, scan_limit_deg=95.0)


class TestRFChainConfig:
    """Tests for RFChainConfig."""

    def test_default_values(self):
        config = RFChainConfig(tx_power_w_per_elem=1.0)
        assert config.pa_efficiency == 0.3
        assert config.noise_figure_db == 3.0
        assert config.n_tx_beams == 1
        assert config.feed_loss_db == 1.0

    def test_invalid_efficiency(self):
        with pytest.raises(ValidationError):
            RFChainConfig(tx_power_w_per_elem=1.0, pa_efficiency=1.5)

    def test_invalid_power(self):
        with pytest.raises(ValidationError):
            RFChainConfig(tx_power_w_per_elem=0)


class TestCostConfig:
    """Tests for CostConfig."""

    def test_default_values(self):
        config = CostConfig()
        assert config.cost_per_elem_usd == 100.0
        assert config.nre_usd == 0.0
        assert config.integration_cost_usd == 0.0

    def test_custom_values(self):
        config = CostConfig(
            cost_per_elem_usd=150.0,
            nre_usd=50000.0,
            integration_cost_usd=10000.0,
        )
        assert config.cost_per_elem_usd == 150.0
        assert config.nre_usd == 50000.0


class TestArchitecture:
    """Tests for the Architecture class."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8),
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
            cost=CostConfig(cost_per_elem_usd=100.0),
            name="Test Array",
        )

    def test_create_architecture(self, sample_architecture):
        assert sample_architecture.array.nx == 8
        assert sample_architecture.rf.tx_power_w_per_elem == 1.0
        assert sample_architecture.n_elements == 64
        assert sample_architecture.name == "Test Array"

    def test_default_cost(self):
        arch = Architecture(
            array=ArrayConfig(nx=4, ny=4),
            rf=RFChainConfig(tx_power_w_per_elem=0.5),
        )
        assert arch.cost.cost_per_elem_usd == 100.0

    def test_model_dump_flat(self, sample_architecture):
        flat = sample_architecture.model_dump_flat()

        assert flat["array.nx"] == 8
        assert flat["array.ny"] == 8
        assert flat["rf.tx_power_w_per_elem"] == 1.0
        assert flat["cost.cost_per_elem_usd"] == 100.0
        assert flat["name"] == "Test Array"

    def test_from_flat(self):
        flat_dict = {
            "array.nx": 16,
            "array.ny": 16,
            "array.geometry": "rectangular",
            "array.dx_lambda": 0.5,
            "array.dy_lambda": 0.5,
            "array.scan_limit_deg": 45.0,
            "rf.tx_power_w_per_elem": 2.0,
            "rf.pa_efficiency": 0.4,
            "rf.noise_figure_db": 2.5,
            "rf.n_tx_beams": 1,
            "rf.feed_loss_db": 0.5,
            "rf.system_loss_db": 0.0,
            "cost.cost_per_elem_usd": 200.0,
            "cost.nre_usd": 10000.0,
            "cost.integration_cost_usd": 5000.0,
            "name": "From Flat",
        }

        arch = Architecture.from_flat(flat_dict)

        assert arch.array.nx == 16
        assert arch.array.scan_limit_deg == 45.0
        assert arch.rf.tx_power_w_per_elem == 2.0
        assert arch.cost.cost_per_elem_usd == 200.0
        assert arch.name == "From Flat"

    def test_round_trip_flat(self, sample_architecture):
        """Test that from_flat(model_dump_flat()) returns equivalent architecture."""
        flat = sample_architecture.model_dump_flat()
        reconstructed = Architecture.from_flat(flat)

        assert reconstructed.array.nx == sample_architecture.array.nx
        assert reconstructed.rf.tx_power_w_per_elem == sample_architecture.rf.tx_power_w_per_elem
        assert reconstructed.cost.cost_per_elem_usd == sample_architecture.cost.cost_per_elem_usd
