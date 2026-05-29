"""
OpenForge — AI-native data engineering platform.

From raw CSV to validated, documented tables with a single command.

SDK usage:
    from openforge import OpenForge

    of = OpenForge()
    of.run("pipeline.yaml", mock=True)
    print(of.tables.list())
    print(of.quality.summary())
"""

__version__ = "0.1.0"
__author__ = "Richard Egidio"

from .sdk import OpenForge, run, infer, status, inspect, heal

__all__ = ["OpenForge", "run", "infer", "status", "inspect", "heal"]
