"""
Base classes for OpenForge plugins.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, runtime_checkable


# Type alias for a custom quality rule function
RuleFunction = Callable[[str, str, str], tuple[bool, str]]
# Signature: (column_name, table_name, warehouse_path) -> (passed, message)


@runtime_checkable
class RuleProtocol(Protocol):
    """Protocol that a rule function must satisfy."""
    def __call__(self, column: str, table: str, warehouse: str) -> tuple[bool, str]: ...


class OpenForgeAgent(ABC):
    """
    Base class for custom pipeline step agents.

    Subclass this to add new step types to OpenForge pipelines.

    Example:
        class DeduplicationAgent(OpenForgeAgent):
            name = "dedup"
            step_type = "dedup"   # matches `type: dedup` in pipeline.yaml

            def run(self, step, context: dict) -> bool:
                table = step.table
                # ... dedup logic ...
                return True
    """

    name: str = "unnamed_agent"
    step_type: str = "custom"      # must match `type:` value in pipeline.yaml
    description: str = ""

    @abstractmethod
    def run(self, step: Any, context: dict) -> bool:
        """
        Execute this agent for a pipeline step.

        Args:
            step: The PipelineStep object from pipeline.yaml.
            context: Dict with project metadata and runtime state.

        Returns:
            True if the step succeeded, False if it failed.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} step_type='{self.step_type}'>"
