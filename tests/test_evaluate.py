"""Tests for the single-case evaluator."""

import pytest

from phased_array_systems.architecture import (
    Architecture,
    ArrayConfig,
    CostConfig,
    RFChainConfig,
)
from phased_array_systems.evaluate import (
    evaluate_case,
    evaluate_case_with_report,
)
from phased_array_systems.requirements import Requirement, RequirementSet
from phased_array_systems.scenarios import CommsLinkScenario


class TestEvaluateCase:
    """Tests for the evaluate_case function."""

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
            cost=CostConfig(
                cost_per_elem_usd=100.0,
                nre_usd=10000.0,
            ),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
            scan_angle_deg=0.0,
        )

    @pytest.fixture
    def sample_requirements(self):
        return RequirementSet(
            requirements=[
                Requirement(
                    id="REQ-001",
                    name="Min EIRP",
                    metric_key="eirp_dbw",
                    op=">=",
                    value=30.0,
                    severity="must",
                ),
                Requirement(
                    id="REQ-002",
                    name="Max Cost",
                    metric_key="cost_usd",
                    op="<=",
                    value=50000.0,
                    severity="must",
                ),
            ]
        )

    def test_basic_evaluation(self, sample_architecture, sample_scenario):
        """Test basic case evaluation without requirements."""
        metrics = evaluate_case(sample_architecture, sample_scenario)

        # Check antenna metrics present
        assert "g_peak_db" in metrics
        assert "beamwidth_az_deg" in metrics
        assert "sll_db" in metrics
        assert "n_elements" in metrics

        # Check comms metrics present
        assert "eirp_dbw" in metrics
        assert "path_loss_db" in metrics
        assert "snr_rx_db" in metrics
        assert "link_margin_db" in metrics

        # Check SWaP-C metrics present
        assert "rf_power_w" in metrics
        assert "prime_power_w" in metrics
        assert "cost_usd" in metrics

        # Check metadata present
        assert "meta.runtime_s" in metrics
        assert metrics["meta.runtime_s"] > 0

    def test_with_case_id(self, sample_architecture, sample_scenario):
        """Test that case_id is included in metrics."""
        metrics = evaluate_case(
            sample_architecture,
            sample_scenario,
            case_id="TEST-001",
        )

        assert metrics["meta.case_id"] == "TEST-001"

    def test_with_requirements_passing(
        self, sample_architecture, sample_scenario, sample_requirements
    ):
        """Test evaluation with passing requirements."""
        metrics = evaluate_case(
            sample_architecture,
            sample_scenario,
            requirements=sample_requirements,
        )

        assert "verification.passes" in metrics
        assert metrics["verification.passes"] == 1.0
        assert metrics["verification.must_pass_count"] == 2.0
        assert metrics["verification.must_total_count"] == 2.0
        assert metrics["verification.failed_ids"] == ""

    def test_with_requirements_failing(self, sample_architecture, sample_scenario):
        """Test evaluation with failing requirements."""
        strict_requirements = RequirementSet(
            requirements=[
                Requirement(
                    id="REQ-001",
                    name="Impossible EIRP",
                    metric_key="eirp_dbw",
                    op=">=",
                    value=100.0,  # Unrealistically high
                    severity="must",
                ),
            ]
        )

        metrics = evaluate_case(
            sample_architecture,
            sample_scenario,
            requirements=strict_requirements,
        )

        assert metrics["verification.passes"] == 0.0
        assert "REQ-001" in metrics["verification.failed_ids"]

    def test_metrics_consistency(self, sample_architecture, sample_scenario):
        """Test that metrics are internally consistent."""
        metrics = evaluate_case(sample_architecture, sample_scenario)

        # n_elements should match array config
        assert metrics["n_elements"] == 64

        # RF power should be n_elements * power_per_elem
        assert metrics["rf_power_w"] == pytest.approx(64.0)

        # Cost should include element cost
        assert metrics["cost_usd"] >= 64 * 100  # At least element cost


class TestEvaluateCaseWithReport:
    """Tests for evaluate_case_with_report function."""

    @pytest.fixture
    def sample_architecture(self):
        return Architecture(
            array=ArrayConfig(nx=8, ny=8),
            rf=RFChainConfig(tx_power_w_per_elem=1.0),
        )

    @pytest.fixture
    def sample_scenario(self):
        return CommsLinkScenario(
            freq_hz=10e9,
            bandwidth_hz=10e6,
            range_m=100e3,
            required_snr_db=10.0,
        )

    @pytest.fixture
    def sample_requirements(self):
        return RequirementSet(
            requirements=[
                Requirement(
                    id="REQ-001",
                    name="Min EIRP",
                    metric_key="eirp_dbw",
                    op=">=",
                    value=30.0,
                ),
            ]
        )

    def test_returns_tuple(
        self, sample_architecture, sample_scenario, sample_requirements
    ):
        """Test that function returns both metrics and report."""
        metrics, report = evaluate_case_with_report(
            sample_architecture,
            sample_scenario,
            sample_requirements,
        )

        assert isinstance(metrics, dict)
        assert hasattr(report, "passes")
        assert hasattr(report, "results")

    def test_report_has_results(
        self, sample_architecture, sample_scenario, sample_requirements
    ):
        """Test that report contains individual results."""
        metrics, report = evaluate_case_with_report(
            sample_architecture,
            sample_scenario,
            sample_requirements,
        )

        assert len(report.results) == 1
        assert report.results[0].requirement.id == "REQ-001"
        assert report.results[0].actual_value is not None
