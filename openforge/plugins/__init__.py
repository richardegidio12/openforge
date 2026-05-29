"""
Plugin API — extend OpenForge with custom rules, agents, and connectors.

Custom quality rule:
    from openforge.plugins import rule

    @rule("email_format")
    def check_email(column: str, table: str, warehouse: str) -> tuple[bool, str]:
        import duckdb, re
        con = duckdb.connect(warehouse)
        values = [r[0] for r in con.execute(
            f'SELECT DISTINCT "{column}" FROM {table} WHERE "{column}" IS NOT NULL'
        ).fetchall()]
        invalid = [v for v in values if not re.match(r'^[^@]+@[^@]+\\.[^@]+$', str(v))]
        return len(invalid) == 0, f"{len(invalid)} invalid email(s) found"

Custom agent:
    from openforge.plugins import OpenForgeAgent

    class MyTransformAgent(OpenForgeAgent):
        name = "my_transform"
        step_type = "my_transform"   # matches `type:` in pipeline.yaml

        def run(self, step, context) -> bool:
            # your logic here
            return True
"""

from .base import OpenForgeAgent, RuleFunction
from .registry import rule, register_agent, get_rule, get_agent, list_rules, list_agents

__all__ = [
    "OpenForgeAgent",
    "RuleFunction",
    "rule",
    "register_agent",
    "get_rule",
    "get_agent",
    "list_rules",
    "list_agents",
]
