"""Defines the tools available to the agent and how they are looked up."""

from datetime import datetime
from typing import Any, Callable
import httpx


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

def get_weather(city: str) -> str:
    """Look up current weather for a named city."""
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10.0,
        )
        geo.raise_for_status()
        places = geo.json().get("results")

        if not places:
            return f"Could not find a place called '{city}'."

        place = places[0]
        lat, lon = place["latitude"], place["longitude"]
        label = f"{place['name']}, {place.get('country', '')}".strip(", ")

        forecast = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=10.0,
        )
        forecast.raise_for_status()
        now = forecast.json()["current"]

        return (
            f"{label}: {now['temperature_2m']}°C, "
            f"humidity {now['relative_humidity_2m']}%, "
            f"wind {now['wind_speed_10m']} km/h"
        )

    except httpx.TimeoutException:
        return "Error: the weather service did not respond in time."
    except httpx.HTTPError as exc:
        return f"Error contacting the weather service: {exc}"
    except (KeyError, ValueError) as exc:
        return f"Error reading the weather response: {exc}"

# Maps tool names to the functions that run them.
TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "get_weather": get_weather,
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
        {
        "name": "get_weather",
        "description": "Get current weather conditions for a city. Use "
                       "whenever the user asks about weather, temperature, "
                       "humidity, or wind anywhere in the world.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "A city name, e.g. 'Lagos' or 'Tokyo'",
                }
            },
            "required": ["city"],
        },
    },
]