"""Hashing utilities for stable case identification."""

import hashlib
import json
from typing import Any


def compute_config_hash(config: dict[str, Any], length: int = 8) -> str:
    """Compute a stable hash for a configuration dictionary.

    Uses JSON serialization with sorted keys to ensure consistent
    ordering, then SHA-256 hashing.

    Args:
        config: Configuration dictionary
        length: Number of hex characters to return

    Returns:
        Hexadecimal hash string
    """
    # Serialize with sorted keys for consistency
    json_str = json.dumps(config, sort_keys=True, default=str)
    hash_bytes = hashlib.sha256(json_str.encode()).hexdigest()
    return hash_bytes[:length]


def compute_case_id(
    case_index: int,
    config: dict[str, Any] | None = None,
    prefix: str = "case",
) -> str:
    """Compute a unique case identifier.

    Args:
        case_index: Sequential case number
        config: Optional configuration to include in hash
        prefix: Prefix for the case ID

    Returns:
        Case ID string like "case_00001" or "case_00001_a1b2c3d4"
    """
    base_id = f"{prefix}_{case_index:05d}"

    if config is not None:
        config_hash = compute_config_hash(config)
        return f"{base_id}_{config_hash}"

    return base_id


def dict_to_hashable(d: dict[str, Any]) -> tuple:
    """Convert a dictionary to a hashable tuple representation.

    Useful for using dictionaries as dictionary keys or in sets.

    Args:
        d: Dictionary to convert

    Returns:
        Tuple of (key, value) pairs, sorted by key
    """
    items = []
    for k in sorted(d.keys()):
        v = d[k]
        if isinstance(v, dict):
            v = dict_to_hashable(v)
        elif isinstance(v, list):
            v = tuple(v)
        items.append((k, v))
    return tuple(items)
