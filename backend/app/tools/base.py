"""Tool base and LangChain adapter.

Tools are plain, directly-testable async classes. ``to_langchain_tool`` adapts any of them
into a LangChain ``StructuredTool`` so agents can bind them for tool-calling, keeping the
tools themselves free of framework coupling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.config.logging import get_logger
from app.domain.exceptions import ToolExecutionError

logger = get_logger(__name__)


class BaseTool(ABC):
    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    async def arun(self, **kwargs: Any) -> Any:
        """Execute the tool with validated keyword arguments."""

    async def safe_arun(self, **kwargs: Any) -> Any:
        """Run with error normalization and logging."""
        try:
            result = await self.arun(**kwargs)
            logger.info("tool.executed", extra={"tool": self.name})
            return result
        except ToolExecutionError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalize to a domain error
            logger.warning("tool.failed", extra={"tool": self.name, "error": str(exc)})
            raise ToolExecutionError(f"Tool '{self.name}' failed: {exc}") from exc


def to_langchain_tool(tool: BaseTool):
    """Adapt a ``BaseTool`` into a LangChain ``StructuredTool``."""
    from langchain_core.tools import StructuredTool

    return StructuredTool.from_function(
        coroutine=tool.safe_arun,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
    )


def build_langchain_tools(tools: list[BaseTool]) -> list:
    """Adapt a list of tools for agent binding."""
    return [to_langchain_tool(t) for t in tools]
