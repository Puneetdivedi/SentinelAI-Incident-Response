"""Analysis tools: read-only SQL and a sandboxed Python evaluator."""

from __future__ import annotations

import contextlib
import io
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.exceptions import ToolExecutionError
from app.tools.base import BaseTool

_FORBIDDEN_SQL = (
    "insert", "update", "delete", "drop", "alter", "create", "truncate",
    "grant", "revoke", "attach", "pragma", "vacuum", "replace",
)


class SqlQueryInput(BaseModel):
    query: str = Field(description="A single read-only SELECT statement.")
    params: dict[str, Any] = Field(default_factory=dict, description="Bound parameters.")
    limit: int = Field(default=100, ge=1, le=1000)


class SqlQueryTool(BaseTool):
    """Executes a single read-only SELECT with bound parameters.

    Injection-safe: statements are validated to be a lone SELECT, DML/DDL keywords are
    rejected, multiple statements are refused, and values pass as bound parameters only.
    """

    name = "sql_query"
    description = "Run a single read-only SELECT against the platform database."
    args_schema = SqlQueryInput

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _validate(query: str) -> str:
        stripped = query.strip().rstrip(";").strip()
        lowered = stripped.lower()
        if ";" in stripped:
            raise ToolExecutionError("Only a single statement is allowed.")
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ToolExecutionError("Only SELECT/CTE queries are permitted.")
        if any(f" {kw} " in f" {lowered} " for kw in _FORBIDDEN_SQL):
            raise ToolExecutionError("Query contains a forbidden (write) keyword.")
        return stripped

    async def arun(self, *, query: str, params: dict | None = None, limit: int = 100) -> list[dict]:
        safe_query = self._validate(query)
        async with self._session_factory() as session:
            result = await session.execute(text(safe_query), params or {})
            rows = result.mappings().all()
        return [dict(row) for row in rows[:limit]]


class PythonExecInput(BaseModel):
    code: str = Field(description="Python expression/statements for numeric analysis.")


class PythonExecutionTool(BaseTool):
    """Sandboxed evaluator for small analysis snippets.

    Runs with a restricted builtin set and no import capability. Intended for arithmetic /
    statistics over already-retrieved evidence, not general code execution. Assign to
    ``result`` or print output.
    """

    name = "python_exec"
    description = "Evaluate a small, safe Python snippet for numeric analysis."
    args_schema = PythonExecInput

    _SAFE_BUILTINS = {
        "abs": abs, "min": min, "max": max, "sum": sum, "len": len, "round": round,
        "sorted": sorted, "range": range, "enumerate": enumerate, "float": float,
        "int": int, "str": str, "list": list, "dict": dict, "set": set, "tuple": tuple,
        "any": any, "all": all, "zip": zip, "map": map, "filter": filter, "print": print,
    }

    async def arun(self, *, code: str) -> dict[str, Any]:
        if "__" in code or "import" in code:
            raise ToolExecutionError("Imports and dunder access are not permitted.")
        namespace: dict[str, Any] = {}
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, {"__builtins__": self._SAFE_BUILTINS}, namespace)  # noqa: S102
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(f"Execution error: {exc}") from exc
        return {
            "result": namespace.get("result"),
            "stdout": stdout.getvalue(),
        }
