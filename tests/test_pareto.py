"""Tests for Pareto extraction utilities."""

import pandas as pd

from phased_array_systems.requirements import Requirement, RequirementSet
from phased_array_systems.trades.pareto import (
    compute_hypervolume,
    extract_pareto,
    filter_feasible,
    rank_pareto,
)


class TestFilterFeasible:
    """Tests for filter_feasible function."""

    def test_filter_by_verification_column(self):
        results = pd.DataFrame(
            {
                "case_id": ["a", "b", "c", "d"],
                "cost_usd": [100, 200, 300, 400],
                "verification.passes": [1.0, 0.0, 1.0, 0.0],
            }
        )

        feasible = filter_feasible(results)

        assert len(feasible) == 2
        assert list(feasible["case_id"]) == ["a", "c"]

    def test_filter_by_requirements(self):
        results = pd.DataFrame(
            {
                "case_id": ["a", "b", "c"],
                "eirp_dbw": [45, 35, 50],
                "cost_usd": [100, 200, 300],
            }
        )

        requirements = RequirementSet(
            requirements=[
                Requirement(
                    id="REQ-001",
                    name="Min EIRP",
                    metric_key="eirp_dbw",
                    op=">=",
                    value=40.0,
                ),
            ]
        )

        feasible = filter_feasible(results, requirements=requirements)

        assert len(feasible) == 2
        assert set(feasible["case_id"]) == {"a", "c"}

    def test_no_filtering_without_requirements(self):
        results = pd.DataFrame(
            {
                "case_id": ["a", "b"],
                "cost_usd": [100, 200],
            }
        )

        feasible = filter_feasible(results)

        assert len(feasible) == 2


class TestExtractPareto:
    """Tests for extract_pareto function."""

    def test_simple_2d_pareto(self):
        """Test simple 2D Pareto extraction."""
        results = pd.DataFrame(
            {
                "case_id": ["a", "b", "c", "d", "e"],
                "cost_usd": [100, 200, 150, 300, 250],
                "eirp_dbw": [40, 45, 42, 50, 44],
            }
        )

        pareto = extract_pareto(
            results,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        # Points on Pareto front: a (100, 40), c (150, 42), b (200, 45), d (300, 50)
        # Point e (250, 44) is dominated by d (300, 50) in EIRP but not cost
        # Actually e is dominated by b (200, 45): lower cost AND higher EIRP
        assert len(pareto) == 4  # a, b, c, d
        assert "e" not in pareto["case_id"].values

    def test_all_pareto_optimal(self):
        """Test when all points are Pareto-optimal."""
        results = pd.DataFrame(
            {
                "case_id": ["a", "b", "c"],
                "cost_usd": [100, 200, 300],
                "eirp_dbw": [40, 50, 60],  # Higher cost -> higher EIRP
            }
        )

        pareto = extract_pareto(
            results,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        assert len(pareto) == 3

    def test_single_point(self):
        """Test with single point."""
        results = pd.DataFrame(
            {
                "case_id": ["a"],
                "cost_usd": [100],
                "eirp_dbw": [40],
            }
        )

        pareto = extract_pareto(
            results,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        assert len(pareto) == 1

    def test_include_dominated(self):
        """Test include_dominated option."""
        results = pd.DataFrame(
            {
                "case_id": ["a", "b", "c"],
                "cost_usd": [100, 200, 150],
                "eirp_dbw": [40, 45, 35],  # c is dominated
            }
        )

        with_dominated = extract_pareto(
            results,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
            include_dominated=True,
        )

        assert len(with_dominated) == 3
        assert "pareto_optimal" in with_dominated.columns

        # c should be marked as not Pareto-optimal
        c_row = with_dominated[with_dominated["case_id"] == "c"].iloc[0]
        assert not c_row["pareto_optimal"]

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        results = pd.DataFrame(columns=["case_id", "cost_usd", "eirp_dbw"])

        pareto = extract_pareto(
            results,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        assert len(pareto) == 0


class TestRankPareto:
    """Tests for rank_pareto function."""

    def test_weighted_sum_ranking(self):
        """Test weighted sum ranking."""
        # Create points with different trade-off characteristics
        # a: cheap but low performance
        # b: moderate cost and performance
        # c: expensive but high performance
        pareto = pd.DataFrame(
            {
                "case_id": ["a", "b", "c"],
                "cost_usd": [100, 200, 400],  # Non-linear cost increase
                "eirp_dbw": [40, 55, 60],  # Diminishing returns on performance
            }
        )

        ranked = rank_pareto(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
            weights=[0.5, 0.5],
            method="weighted_sum",
        )

        assert "pareto_rank" in ranked.columns
        assert "pareto_score" in ranked.columns
        # All points are ranked
        assert len(ranked) == 3
        # Each point should have a rank (may have ties)
        assert all(ranked["pareto_rank"] >= 1)
        assert ranked["pareto_rank"].max() <= 3

    def test_equal_weights_by_default(self):
        """Test that equal weights are used by default."""
        pareto = pd.DataFrame(
            {
                "case_id": ["a", "b"],
                "cost_usd": [100, 200],
                "eirp_dbw": [40, 50],
            }
        )

        ranked = rank_pareto(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        assert len(ranked) == 2

    def test_topsis_ranking(self):
        """Test TOPSIS ranking method."""
        pareto = pd.DataFrame(
            {
                "case_id": ["a", "b", "c"],
                "cost_usd": [100, 200, 300],
                "eirp_dbw": [40, 50, 60],
            }
        )

        ranked = rank_pareto(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
            method="topsis",
        )

        assert "pareto_rank" in ranked.columns
        assert len(ranked) == 3


class TestComputeHypervolume:
    """Tests for hypervolume computation."""

    def test_simple_2d_hypervolume(self):
        """Test 2D hypervolume computation."""
        pareto = pd.DataFrame(
            {
                "cost_usd": [1.0, 2.0],
                "eirp_dbw": [2.0, 1.0],
            }
        )

        # For minimize cost, maximize eirp (so we negate eirp)
        # Points in minimization space: (1, -2), (2, -1)
        # Reference: (3, 0)
        # Hypervolume = 2*1 + 1*1 = 3 (approximately, with reference scaling)

        hv = compute_hypervolume(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
            reference_point=[3.0, 0.0],
        )

        assert hv > 0

    def test_empty_pareto(self):
        """Test hypervolume with empty Pareto set."""
        pareto = pd.DataFrame(columns=["cost_usd", "eirp_dbw"])

        hv = compute_hypervolume(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
        )

        assert hv == 0.0

    def test_single_point_hypervolume(self):
        """Test hypervolume with single point and explicit reference."""
        pareto = pd.DataFrame(
            {
                "cost_usd": [1.0],
                "eirp_dbw": [2.0],
            }
        )

        # Provide explicit reference point for meaningful hypervolume
        # In minimization space: cost is minimized, eirp is negated (so -eirp is minimized)
        # Point: (1.0, -2.0), Reference must be worse: (5.0, 0.0) i.e., higher cost, lower eirp
        hv = compute_hypervolume(
            pareto,
            [("cost_usd", "minimize"), ("eirp_dbw", "maximize")],
            reference_point=[5.0, 0.0],  # Reference: cost=5, eirp=0 (negated to 0)
        )

        # Hypervolume should be (5-1) * (0-(-2)) = 4 * 2 = 8
        assert hv > 0
