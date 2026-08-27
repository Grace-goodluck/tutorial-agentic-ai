"""Defines the tools available to the agent and how they are looked up."""

from datetime import datetime
from typing import Any, Callable


def get_current_time() -> str:
    """Return the current date and time as a readable string."""
    return datetime.now().strftime("%A, %d %B %Y at %H:%M")


def calculate(expression: str) -> str:
    """Evaluate a simple arithmetic expression."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression).issubset(allowed):
        return "Error: only numbers and + - * / ( ) are permitted."
    try:
        return str(eval(expression))
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


# Maps tool names to the functions that run them.
TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}

# Descriptions the model reads to decide which tool to call.
TOOL_SCHEMAS: list[dict] = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time. Use when the user asks "
                       "about today's date, the current time, or anything "
                       "requiring knowledge of now.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "calculate",
        "description": "Evaluate an arithmetic expression. Use for any "
                       "calculation rather than working it out yourself.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "An arithmetic expression, e.g. '847 * 293'",
                }
            },
            "required": ["expression"],
        },
    },
]