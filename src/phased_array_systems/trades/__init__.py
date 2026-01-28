"""Trade study tools: DOE, batch evaluation, Pareto analysis."""

from phased_array_systems.trades.design_space import DesignSpace, DesignVariable
from phased_array_systems.trades.doe import generate_doe
from phased_array_systems.trades.pareto import extract_pareto, filter_feasible, rank_pareto
from phased_array_systems.trades.runner import BatchRunner

__all__ = [
    "DesignSpace",
    "DesignVariable",
    "generate_doe",
    "BatchRunner",
    "extract_pareto",
    "filter_feasible",
    "rank_pareto",
]
