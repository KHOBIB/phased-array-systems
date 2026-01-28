"""Tests for visualization functions."""

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for testing
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from phased_array_systems.viz import pareto_plot, scatter_matrix


class TestParetoPlot:
    """Tests for pareto_plot function."""

    @pytest.fixture
    def sample_results(self):
        return pd.DataFrame(
            {
                "case_id": [f"case_{i}" for i in range(20)],
                "cost_usd": [100 + i * 10 for i in range(20)],
                "eirp_dbw": [40 + i * 0.5 for i in range(20)],
                "link_margin_db": [5 + i * 0.2 for i in range(20)],
            }
        )

    @pytest.fixture
    def sample_pareto(self):
        return pd.DataFrame(
            {
                "case_id": ["p1", "p2", "p3"],
                "cost_usd": [100, 150, 200],
                "eirp_dbw": [40, 45, 50],
            }
        )

    def test_basic_plot(self, sample_results):
        """Test basic Pareto plot creation."""
        fig = pareto_plot(sample_results, x="cost_usd", y="eirp_dbw")

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_pareto_front(self, sample_results, sample_pareto):
        """Test plot with highlighted Pareto front."""
        fig = pareto_plot(
            sample_results,
            x="cost_usd",
            y="eirp_dbw",
            pareto_front=sample_pareto,
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_feasibility_mask(self, sample_results):
        """Test plot with feasibility mask."""
        mask = pd.Series([i % 2 == 0 for i in range(len(sample_results))])

        fig = pareto_plot(
            sample_results,
            x="cost_usd",
            y="eirp_dbw",
            feasible_mask=mask,
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_color_by(self, sample_results):
        """Test plot colored by a metric."""
        fig = pareto_plot(
            sample_results,
            x="cost_usd",
            y="eirp_dbw",
            color_by="link_margin_db",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_labels(self, sample_results):
        """Test plot with custom labels."""
        fig = pareto_plot(
            sample_results,
            x="cost_usd",
            y="eirp_dbw",
            title="My Trade Study",
            x_label="System Cost (USD)",
            y_label="EIRP (dBW)",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_figure(self, sample_results):
        """Test saving figure to file."""
        from phased_array_systems.viz.plots import save_figure

        fig = pareto_plot(sample_results, x="cost_usd", y="eirp_dbw")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_plot.png"
            save_figure(fig, str(path))
            assert path.exists()

        plt.close(fig)


class TestScatterMatrix:
    """Tests for scatter_matrix function."""

    @pytest.fixture
    def sample_results(self):
        return pd.DataFrame(
            {
                "cost_usd": [100 + i * 10 for i in range(50)],
                "eirp_dbw": [40 + i * 0.5 for i in range(50)],
                "link_margin_db": [5 + i * 0.2 for i in range(50)],
                "prime_power_w": [200 + i * 5 for i in range(50)],
            }
        )

    def test_basic_scatter_matrix(self, sample_results):
        """Test basic scatter matrix creation."""
        fig = scatter_matrix(
            sample_results,
            columns=["cost_usd", "eirp_dbw", "link_margin_db"],
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_color_by(self, sample_results):
        """Test scatter matrix with coloring."""
        fig = scatter_matrix(
            sample_results,
            columns=["cost_usd", "eirp_dbw"],
            color_by="link_margin_db",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_histogram_diagonal(self, sample_results):
        """Test scatter matrix with histogram diagonal."""
        fig = scatter_matrix(
            sample_results,
            columns=["cost_usd", "eirp_dbw"],
            diagonal="hist",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_title(self, sample_results):
        """Test scatter matrix with title."""
        fig = scatter_matrix(
            sample_results,
            columns=["cost_usd", "eirp_dbw"],
            title="Trade Space Exploration",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)
