"""Configuration file loading utilities."""

import json
from pathlib import Path

import yaml

from phased_array_systems.io.schema import StudyConfig


def load_config(path: str | Path) -> StudyConfig:
    """Load a study configuration from a YAML or JSON file.

    Args:
        path: Path to configuration file (.yaml, .yml, or .json)

    Returns:
        Validated StudyConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file format is not supported
        ValidationError: If config validation fails
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    elif suffix == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported config format: {suffix}. Use .yaml, .yml, or .json")

    return StudyConfig.model_validate(data)


def load_config_from_string(content: str, format: str = "yaml") -> StudyConfig:
    """Load a study configuration from a string.

    Args:
        content: Configuration content as string
        format: Format of the content ("yaml" or "json")

    Returns:
        Validated StudyConfig object
    """
    if format.lower() in ("yaml", "yml"):
        data = yaml.safe_load(content)
    elif format.lower() == "json":
        data = json.loads(content)
    else:
        raise ValueError(f"Unsupported format: {format}")

    return StudyConfig.model_validate(data)


def save_config(config: StudyConfig, path: str | Path, format: str | None = None) -> None:
    """Save a study configuration to a file.

    Args:
        config: StudyConfig object to save
        path: Output file path
        format: Output format (auto-detected from extension if None)
    """
    path = Path(path)

    if format is None:
        format = path.suffix.lower().lstrip(".")

    data = config.model_dump(exclude_none=True)

    if format in ("yaml", "yml"):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    elif format == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
