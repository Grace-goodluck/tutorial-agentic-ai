"""Gemini implementation of the ModelProvider contract."""

import time
from typing import Any

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from .. import config
from .base import ModelProvider


class GeminiProvider(ModelProvider):
    """Talks to Google's Gemini API."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=config.get_api_key())
        self.model_name = config.MODEL_NAME

    def send(self, messages: list[dict], tools: list[dict] | None = None) -> Any:
        """Send the conversation to Gemini, retrying transient failures."""
        request_config = None
        if tools:
            request_config = types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=tools)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )

        delay = config.RETRY_BASE_DELAY
        last_error: Exception | None = None

        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=messages,
                    config=request_config,
                )
            except genai_errors.ServerError as exc:
                last_error = exc
                if attempt == config.MAX_RETRIES:
                    break
                print(
                    f"  [provider] attempt {attempt} failed "
                    f"({exc.code}); retrying in {delay:.0f}s"
                )
                time.sleep(delay)
                delay *= 2

        raise RuntimeError(
            f"Gemini unavailable after {config.MAX_RETRIES} attempts: {last_error}"
        )
        