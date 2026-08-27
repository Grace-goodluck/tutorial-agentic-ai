"""Defines the contract every model provider must satisfy."""

from abc import ABC, abstractmethod
from typing import Any


class ModelProvider(ABC):
    """Base class for all LLM providers.

    The agent talks only to this interface, never to a specific SDK.
    """

    @abstractmethod
    def send(self, messages: list[dict], tools: list[dict] | None = None) -> Any:
        """Send a conversation to the model and return its raw response."""
        ...