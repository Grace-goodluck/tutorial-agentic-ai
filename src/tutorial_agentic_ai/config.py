"""Central configuration for the agent application."""

import os
from dotenv import load_dotenv

load_dotenv()

# Which provider the agent talks to. Change this to swap models.
PROVIDER = "gemini"

# The specific model. Update here if a model is retired.
MODEL_NAME = "gemini-3.6-flash"

# Safety limit: how many tool calls before the agent gives up.
MAX_ITERATIONS = 10

# Retry behaviour for transient API failures.
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds; doubles after each failed attempt


def get_api_key() -> str:
    """Read the API key from the environment, failing clearly if absent."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Create a .env file in the project "
            "root containing: GEMINI_API_KEY=your_key_here"
        )
    return key