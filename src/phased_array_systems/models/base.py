"""Base model block protocol and utilities."""

from typing import Any, Protocol, runtime_checkable

from phased_array_systems.types import MetricsDict, Scenario


@runtime_checkable
class ModelBlock(Protocol):
    """Protocol for model blocks that evaluate architecture/scenario combinations.

    All model blocks must implement evaluate() and return a flat metrics dictionary.
    The metrics dictionary uses the canonical metric keys defined in the package
    documentation.
    """

    name: str

    def evaluate(self, arch: Any, scenario: Scenario, context: dict[str, Any]) -> MetricsDict:
        """Evaluate the model and return metrics.

        Args:
            arch: Architecture configuration object
            scenario: Scenario configuration object
            context: Additional context (e.g., results from other models)

        Returns:
            Dictionary of metric_name -> value pairs
        """
        ...
