"""Gemini implementation of the ModelProvider contract."""

from typing import Any

from google import genai
from google.genai import types

from .. import config
from .base import ModelProvider


class GeminiProvider(ModelProvider):
    """Talks to Google's Gemini API."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=config.get_api_key())
        self.model_name = config.MODEL_NAME

    def send(self, messages: list[dict], tools: list[dict] | None = None) -> Any:
        """Send the conversation to Gemini and return the raw response."""
        request_config = None
        if tools:
            request_config = types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=tools)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )

        return self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=request_config,
        )