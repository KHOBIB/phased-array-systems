"""Command-line interface for phased-array-systems.

Planned for Phase 4 implementation.
"""

import sys


def main():
    """Entry point for the pasys CLI."""
    print("phased-array-systems CLI")
    print("=" * 40)
    print("CLI implementation planned for Phase 4.")
    print()
    print("For now, use the Python API directly:")
    print("  - Single case: examples/01_comms_single_case.py")
    print("  - DOE study: examples/02_comms_doe_trade.py")
    print()
    print("See documentation at:")
    print("  https://github.com/phased-array-systems/phased-array-systems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
