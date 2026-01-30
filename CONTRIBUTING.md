# Contributing to phased-array-systems

Thank you for your interest in contributing to phased-array-systems! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/phased-array-systems.git
   cd phased-array-systems
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev,docs,plotting]"
   ```

4. **Verify the installation:**
   ```bash
   pytest tests/ -v
   ```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=phased_array_systems

# Run a specific test file
pytest tests/test_link_budget.py -v
```

### Code Quality

We use `ruff` for linting and formatting, and `mypy` for type checking:

```bash
# Lint the codebase
ruff check .

# Auto-format code
ruff format .

# Type check
mypy src/phased_array_systems
```

## Making Changes

### Branching Strategy

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear, atomic commits

3. Push to your fork and create a Pull Request

### Commit Messages

Write clear, descriptive commit messages:

```
Add support for triangular array geometry

- Implement triangular element positioning
- Add tests for new geometry type
- Update documentation with examples
```

### Pull Request Guidelines

- **Title:** Use a clear, descriptive title
- **Description:** Explain what changes you made and why
- **Tests:** Add tests for new functionality
- **Documentation:** Update docs if adding new features
- **Small PRs:** Keep changes focused; large changes should be split into multiple PRs

## What to Contribute

### Good First Issues

Look for issues labeled `good first issue` - these are ideal for newcomers.

### Areas We Need Help

- **New models:** Additional propagation models, antenna patterns
- **Documentation:** Tutorials, examples, API docs improvements
- **Testing:** Increase test coverage, add edge case tests
- **Performance:** Optimization of batch evaluation, caching improvements
- **Visualization:** New plot types, interactive visualizations

### Feature Requests

Before starting on a large feature:
1. Check existing issues to avoid duplicates
2. Open an issue describing the feature
3. Wait for discussion/approval before implementing

## Code Style

### Python Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for all public functions
- Use Google-style docstrings
- Keep functions focused and under 50 lines when possible

### Docstring Example

```python
def compute_link_margin(
    eirp_dbw: float,
    path_loss_db: float,
    required_snr_db: float,
) -> dict[str, float]:
    """Compute the communications link margin.

    Calculates received SNR and margin to the required threshold
    for a point-to-point link.

    Args:
        eirp_dbw: Effective Isotropic Radiated Power in dBW.
        path_loss_db: Total path loss in dB.
        required_snr_db: Required SNR for demodulation in dB.

    Returns:
        Dictionary containing:
            - snr_db: Received signal-to-noise ratio
            - margin_db: Margin above required SNR (positive = passes)

    Raises:
        ValueError: If any input is NaN or infinite.

    Example:
        >>> result = compute_link_margin(50.0, 150.0, 10.0)
        >>> print(f"Margin: {result['margin_db']:.1f} dB")
    """
```

### Testing Guidelines

- Test both happy path and edge cases
- Use descriptive test names: `test_extract_pareto_with_empty_dataframe`
- Use pytest fixtures for shared setup
- Mock external dependencies (e.g., `phased-array-modeling`)

## Documentation

### Building Docs Locally

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve locally with live reload
mkdocs serve

# Build static site
mkdocs build
```

### Documentation Structure

- `docs/getting-started/` - Installation and quickstart
- `docs/user-guide/` - Detailed usage guides
- `docs/tutorials/` - Step-by-step tutorials
- `docs/api/` - API reference (auto-generated from docstrings)
- `docs/theory/` - Background theory and equations

## Release Process

Releases are managed by maintainers:

1. Update `__about__.py` with new version
2. Update `CHANGELOG.md`
3. Create a GitHub release with tag `vX.Y.Z`
4. GitHub Actions will publish to PyPI

## Getting Help

- **Questions:** Open a GitHub Discussion
- **Bugs:** Open a GitHub Issue
- **Security:** Email maintainers directly (do not open public issues)

## Recognition

Contributors are recognized in:
- The GitHub contributors page
- Release notes for significant contributions
- The project README for major contributions

Thank you for contributing to phased-array-systems!
