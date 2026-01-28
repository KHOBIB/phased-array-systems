"""Tests for the requirements subsystem."""

import pytest

from phased_array_systems.requirements import (
    Requirement,
    RequirementSet,
    VerificationReport,
)


class TestRequirement:
    """Tests for the Requirement class."""

    def test_create_requirement(self):
        req = Requirement(
            id="REQ-001",
            name="Minimum EIRP",
            metric_key="eirp_dbw",
            op=">=",
            value=40.0,
            units="dBW",
            severity="must",
        )
        assert req.id == "REQ-001"
        assert req.metric_key == "eirp_dbw"
        assert req.op == ">="
        assert req.value == 40.0

    @pytest.mark.parametrize(
        "op,threshold,actual,expected",
        [
            (">=", 40.0, 45.0, True),
            (">=", 40.0, 40.0, True),
            (">=", 40.0, 35.0, False),
            ("<=", 100.0, 90.0, True),
            ("<=", 100.0, 100.0, True),
            ("<=", 100.0, 110.0, False),
            (">", 40.0, 45.0, True),
            (">", 40.0, 40.0, False),
            ("<", 100.0, 90.0, True),
            ("<", 100.0, 100.0, False),
            ("==", 50.0, 50.0, True),
            ("==", 50.0, 50.1, False),
        ],
    )
    def test_check_operators(self, op, threshold, actual, expected):
        req = Requirement(
            id="REQ-TEST",
            name="Test Req",
            metric_key="test_metric",
            op=op,
            value=threshold,
        )
        assert req.check(actual) == expected

    def test_compute_margin_gte(self):
        req = Requirement(
            id="REQ-001",
            name="Min EIRP",
            metric_key="eirp_dbw",
            op=">=",
            value=40.0,
        )
        assert req.compute_margin(45.0) == 5.0
        assert req.compute_margin(35.0) == -5.0

    def test_compute_margin_lte(self):
        req = Requirement(
            id="REQ-002",
            name="Max Cost",
            metric_key="cost_usd",
            op="<=",
            value=10000.0,
        )
        assert req.compute_margin(8000.0) == 2000.0
        assert req.compute_margin(12000.0) == -2000.0


class TestRequirementSet:
    """Tests for the RequirementSet class."""

    @pytest.fixture
    def sample_requirements(self):
        return RequirementSet(
            requirements=[
                Requirement(
                    id="REQ-001",
                    name="Minimum EIRP",
                    metric_key="eirp_dbw",
                    op=">=",
                    value=40.0,
                    severity="must",
                ),
                Requirement(
                    id="REQ-002",
                    name="Maximum Cost",
                    metric_key="cost_usd",
                    op="<=",
                    value=10000.0,
                    severity="must",
                ),
                Requirement(
                    id="REQ-003",
                    name="Preferred Link Margin",
                    metric_key="link_margin_db",
                    op=">=",
                    value=6.0,
                    severity="should",
                ),
            ],
            name="Test Requirements",
        )

    def test_verify_all_pass(self, sample_requirements):
        metrics = {
            "eirp_dbw": 45.0,
            "cost_usd": 8000.0,
            "link_margin_db": 8.0,
        }
        report = sample_requirements.verify(metrics)

        assert report.passes is True
        assert len(report.failed_ids) == 0
        assert report.must_pass_count == 2
        assert report.must_total_count == 2

    def test_verify_must_fails(self, sample_requirements):
        metrics = {
            "eirp_dbw": 35.0,  # Below threshold
            "cost_usd": 8000.0,
            "link_margin_db": 8.0,
        }
        report = sample_requirements.verify(metrics)

        assert report.passes is False
        assert "REQ-001" in report.failed_ids
        assert report.must_pass_count == 1
        assert report.must_total_count == 2

    def test_verify_should_fails_but_passes_overall(self, sample_requirements):
        metrics = {
            "eirp_dbw": 45.0,
            "cost_usd": 8000.0,
            "link_margin_db": 4.0,  # Below threshold but severity="should"
        }
        report = sample_requirements.verify(metrics)

        assert report.passes is True  # "should" failures don't fail overall
        assert "REQ-003" in report.failed_ids
        assert report.should_pass_count == 0
        assert report.should_total_count == 1

    def test_verify_missing_metric(self, sample_requirements):
        metrics = {
            "eirp_dbw": 45.0,
            # cost_usd missing
            "link_margin_db": 8.0,
        }
        report = sample_requirements.verify(metrics)

        assert report.passes is False
        assert "REQ-002" in report.failed_ids
        # Find the result for REQ-002
        req002_result = next(r for r in report.results if r.requirement.id == "REQ-002")
        assert req002_result.error is not None
        assert "not found" in req002_result.error

    def test_add_requirement(self):
        req_set = RequirementSet(name="Dynamic Set")
        req_set.add(
            Requirement(
                id="REQ-NEW",
                name="New Req",
                metric_key="new_metric",
                op=">=",
                value=10.0,
            )
        )
        assert len(req_set) == 1

    def test_get_by_id(self, sample_requirements):
        req = sample_requirements.get_by_id("REQ-002")
        assert req is not None
        assert req.name == "Maximum Cost"

        req_none = sample_requirements.get_by_id("REQ-NONEXISTENT")
        assert req_none is None

    def test_report_to_dict(self, sample_requirements):
        metrics = {
            "eirp_dbw": 45.0,
            "cost_usd": 8000.0,
            "link_margin_db": 8.0,
        }
        report = sample_requirements.verify(metrics)
        report_dict = report.to_dict()

        assert report_dict["passes"] is True
        assert len(report_dict["results"]) == 3
        assert report_dict["must_pass_count"] == 2


class TestVerificationReport:
    """Tests for VerificationReport."""

    def test_report_structure(self):
        req = Requirement(
            id="REQ-001",
            name="Test",
            metric_key="test",
            op=">=",
            value=10.0,
        )
        from phased_array_systems.requirements.core import RequirementResult

        result = RequirementResult(
            requirement=req,
            actual_value=15.0,
            passes=True,
            margin=5.0,
        )
        report = VerificationReport(
            passes=True,
            results=[result],
            failed_ids=[],
            must_pass_count=1,
            must_total_count=1,
        )

        assert report.passes is True
        assert len(report.results) == 1
        assert report.results[0].margin == 5.0
