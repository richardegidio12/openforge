"""
Plugin Registry — stores and retrieves custom rules and agents.

Plugins are registered either via:
  1. @rule decorator
  2. register_agent() function
  3. Entry points in pyproject.toml (auto-discovery, Phase 5+)
"""

from __future__ import annotations

from typing import Callable, Type

from .base import OpenForgeAgent, RuleFunction

# Global registries
_rules: dict[str, RuleFunction] = {}
_agents: dict[str, Type[OpenForgeAgent]] = {}


# ---------------------------------------------------------------------------
# Rule registration
# ---------------------------------------------------------------------------

def rule(name: str):
    """
    Decorator to register a custom quality rule.

    The rule function receives (column_name, table_name, warehouse_path)
    and must return (passed: bool, message: str).

    Example:
        @rule("positive_value")
        def check_positive(column: str, table: str, warehouse: str):
            import duckdb
            con = duckdb.connect(warehouse)
            count = con.execute(
                f'SELECT COUNT(*) FROM {table} WHERE "{column}" < 0'
            ).fetchone()[0]
            return count == 0, f"{count} negative value(s) found"

    Usage in pipeline.yaml:
        rules:
          - column: amount
            checks: [positive_value]
    """
    def decorator(fn: RuleFunction) -> RuleFunction:
        _rules[name] = fn
        return fn
    return decorator


def get_rule(name: str) -> RuleFunction | None:
    """Return a registered rule by name, or None if not found."""
    return _rules.get(name)


def list_rules() -> list[str]:
    """Return names of all registered custom rules."""
    return sorted(_rules.keys())


# ---------------------------------------------------------------------------
# Agent registration
# ---------------------------------------------------------------------------

def register_agent(agent_class: Type[OpenForgeAgent]) -> Type[OpenForgeAgent]:
    """
    Register a custom agent class.

    Can be used as a decorator:
        @register_agent
        class MyAgent(OpenForgeAgent):
            step_type = "my_step"
            ...
    """
    _agents[agent_class.step_type] = agent_class
    return agent_class


def get_agent(step_type: str) -> Type[OpenForgeAgent] | None:
    """Return a registered agent class by step_type, or None."""
    return _agents.get(step_type)


def list_agents() -> list[str]:
    """Return step_type names of all registered custom agents."""
    return sorted(_agents.keys())
