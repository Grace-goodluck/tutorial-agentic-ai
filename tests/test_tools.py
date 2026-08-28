"""Tests for the tool functions and registry."""

from tutorial_agentic_ai.tools.registry import (
    TOOL_FUNCTIONS,
    TOOL_SCHEMAS,
    calculate,
    get_current_time,
)


def test_calculate_handles_basic_arithmetic():
    assert calculate("847 * 293") == "248171"
    assert calculate("2 + 2") == "4"


def test_calculate_rejects_unsafe_input():
    result = calculate("__import__('os').system('dir')")
    assert result.startswith("Error")


def test_calculate_reports_bad_expressions_without_crashing():
    result = calculate("5 / 0")
    assert result.startswith("Error")


def test_get_current_time_returns_a_string():
    result = get_current_time()
    assert isinstance(result, str)
    assert len(result) > 0


def test_every_schema_has_a_matching_function():
    for schema in TOOL_SCHEMAS:
        assert schema["name"] in TOOL_FUNCTIONS


def test_every_function_has_a_matching_schema():
    schema_names = {schema["name"] for schema in TOOL_SCHEMAS}
    for name in TOOL_FUNCTIONS:
        assert name in schema_names