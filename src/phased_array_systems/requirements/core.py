"""Core requirement and verification classes."""

from dataclasses import dataclass, field

from phased_array_systems.types import ComparisonOp, MetricsDict, Severity


@dataclass(frozen=True)
class Requirement:
    """A single requirement specification.

    Attributes:
        id: Unique identifier for the requirement (e.g., "REQ-001")
        name: Human-readable name
        metric_key: The key in the metrics dictionary to check
        op: Comparison operator
        value: Threshold value to compare against
        units: Optional units string for documentation
        severity: Importance level ("must", "should", "nice")
    """

    id: str
    name: str
    metric_key: str
    op: ComparisonOp
    value: float
    units: str | None = None
    severity: Severity = "must"

    def check(self, actual_value: float) -> bool:
        """Check if the actual value satisfies this requirement.

        Args:
            actual_value: The measured/computed value to check

        Returns:
            True if requirement is satisfied, False otherwise
        """
        if self.op == ">=":
            return actual_value >= self.value
        elif self.op == "<=":
            return actual_value <= self.value
        elif self.op == "==":
            return actual_value == self.value
        elif self.op == ">":
            return actual_value > self.value
        elif self.op == "<":
            return actual_value < self.value
        else:
            raise ValueError(f"Unknown operator: {self.op}")

    def compute_margin(self, actual_value: float) -> float:
        """Compute the margin to the requirement threshold.

        Positive margin means the requirement is satisfied with room to spare.
        Negative margin means the requirement is not met.

        Args:
            actual_value: The measured/computed value

        Returns:
            Margin value (interpretation depends on operator)
        """
        if self.op in (">=", ">"):
            return actual_value - self.value
        elif self.op in ("<=", "<"):
            return self.value - actual_value
        else:  # ==
            return -abs(actual_value - self.value)


@dataclass
class RequirementResult:
    """Result of checking a single requirement.

    Attributes:
        requirement: The requirement that was checked
        actual_value: The actual value from metrics (None if metric missing)
        passes: Whether the requirement passed
        margin: Margin to the threshold
        error: Error message if metric was missing or check failed
    """

    requirement: Requirement
    actual_value: float | None
    passes: bool
    margin: float | None
    error: str | None = None


@dataclass
class VerificationReport:
    """Complete verification report for a set of requirements.

    Attributes:
        passes: True if ALL 'must' requirements pass
        results: List of individual requirement results
        failed_ids: List of requirement IDs that failed
        must_pass_count: Number of must requirements that passed
        must_total_count: Total number of must requirements
        should_pass_count: Number of should requirements that passed
        should_total_count: Total number of should requirements
    """

    passes: bool
    results: list[RequirementResult]
    failed_ids: list[str]
    must_pass_count: int = 0
    must_total_count: int = 0
    should_pass_count: int = 0
    should_total_count: int = 0

    def to_dict(self) -> dict:
        """Convert report to dictionary for serialization."""
        return {
            "passes": self.passes,
            "failed_ids": self.failed_ids,
            "must_pass_count": self.must_pass_count,
            "must_total_count": self.must_total_count,
            "should_pass_count": self.should_pass_count,
            "should_total_count": self.should_total_count,
            "results": [
                {
                    "id": r.requirement.id,
                    "name": r.requirement.name,
                    "metric_key": r.requirement.metric_key,
                    "threshold": r.requirement.value,
                    "operator": r.requirement.op,
                    "actual_value": r.actual_value,
                    "passes": r.passes,
                    "margin": r.margin,
                    "severity": r.requirement.severity,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


@dataclass
class RequirementSet:
    """A collection of requirements with verification capabilities.

    Attributes:
        requirements: List of requirements
        name: Optional name for the requirement set
    """

    requirements: list[Requirement] = field(default_factory=list)
    name: str | None = None

    def add(self, requirement: Requirement) -> None:
        """Add a requirement to the set."""
        self.requirements.append(requirement)

    def verify(self, metrics: MetricsDict) -> VerificationReport:
        """Verify all requirements against provided metrics.

        Args:
            metrics: Dictionary of metric_name -> value

        Returns:
            VerificationReport with pass/fail status and margins
        """
        results: list[RequirementResult] = []
        failed_ids: list[str] = []
        must_pass = 0
        must_total = 0
        should_pass = 0
        should_total = 0

        for req in self.requirements:
            # Track totals by severity
            if req.severity == "must":
                must_total += 1
            elif req.severity == "should":
                should_total += 1

            # Check if metric exists
            if req.metric_key not in metrics:
                result = RequirementResult(
                    requirement=req,
                    actual_value=None,
                    passes=False,
                    margin=None,
                    error=f"Metric '{req.metric_key}' not found in results",
                )
                failed_ids.append(req.id)
            else:
                actual = metrics[req.metric_key]
                if actual is None or not isinstance(actual, (int, float)):
                    result = RequirementResult(
                        requirement=req,
                        actual_value=None,
                        passes=False,
                        margin=None,
                        error=f"Metric '{req.metric_key}' has invalid value: {actual}",
                    )
                    failed_ids.append(req.id)
                else:
                    actual_float = float(actual)
                    passes = req.check(actual_float)
                    margin = req.compute_margin(actual_float)
                    result = RequirementResult(
                        requirement=req,
                        actual_value=actual_float,
                        passes=passes,
                        margin=margin,
                    )
                    if not passes:
                        failed_ids.append(req.id)
                    else:
                        if req.severity == "must":
                            must_pass += 1
                        elif req.severity == "should":
                            should_pass += 1

            results.append(result)

        # Overall pass requires all "must" requirements to pass
        all_must_pass = must_pass == must_total

        return VerificationReport(
            passes=all_must_pass,
            results=results,
            failed_ids=failed_ids,
            must_pass_count=must_pass,
            must_total_count=must_total,
            should_pass_count=should_pass,
            should_total_count=should_total,
        )

    def get_by_id(self, req_id: str) -> Requirement | None:
        """Get a requirement by its ID."""
        for req in self.requirements:
            if req.id == req_id:
                return req
        return None

    def __len__(self) -> int:
        return len(self.requirements)

    def __iter__(self):
        return iter(self.requirements)
