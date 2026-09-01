"""The agent control loop."""

import json
import logging

from google.genai import types

from . import config
from .providers.gemini import GeminiProvider
from .tools.registry import TOOL_FUNCTIONS, TOOL_SCHEMAS
logger = logging.getLogger(__name__)

class Agent:
    """Runs the reason-act loop: model decides, tools execute, repeat."""

    def __init__(self, verbose: bool = True) -> None:
        self.provider = GeminiProvider()
        self.verbose = verbose
        self.messages: list = []

    def _log(self, message: str) -> None:
        if self.verbose:
            logger.info(message)

    def _serialise(self) -> list[dict]:
        """Convert messages into plain dictionaries for storage."""
        stored = []
        for message in self.messages:
            for part in message.parts:
                if part.text:
                    stored.append({"role": message.role, "text": part.text})
        return stored

    def load_history(self) -> None:
        """Restore previous conversation from disk, if any exists."""
        if not config.HISTORY_FILE.exists():
            return
        try:
            raw = json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("could not read history: %s", exc)
            return

        self.messages = [
            types.Content(
                role=item["role"], parts=[types.Part(text=item["text"])]
            )
            for item in raw
        ]
        logger.info("restored %d messages from previous sessions", len(self.messages))

    def save_history(self) -> None:
        """Write the conversation to disk."""
        try:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            config.HISTORY_FILE.write_text(
                json.dumps(self._serialise(), indent=2), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("could not save history: %s", exc)

    def clear_history(self) -> None:
        """Forget everything, in memory and on disk."""
        self.messages = []
        config.HISTORY_FILE.unlink(missing_ok=True)
        logger.info("history cleared")        

    def run(self, user_input: str) -> str:
        """Handle one user request, looping through tool calls as needed."""
        self.messages.append(
            types.Content(role="user", parts=[types.Part(text=user_input)])
        )

        for iteration in range(config.MAX_ITERATIONS):
            self._log(f"iteration {iteration + 1}: asking the model")

            response = self.provider.send(self.messages, TOOL_SCHEMAS)
            candidate = response.candidates[0].content
            self.messages.append(candidate)

            tool_calls = [p.function_call for p in candidate.parts if p.function_call]

            if not tool_calls:
                self._log("model returned a final answer")
                return candidate.parts[0].text

            results = []
            for call in tool_calls:
                self._log(f"model requested tool: {call.name}({dict(call.args)})")
                result = self._execute_tool(call.name, dict(call.args))
                self._log(f"tool returned: {result}")
                results.append(
                    types.Part.from_function_response(
                        name=call.name, response={"result": result}
                    )
                )

            self.messages.append(types.Content(role="user", parts=results))

        return "Stopped: reached the maximum number of tool calls."

    def _execute_tool(self, name: str, args: dict) -> str:
        """Look up and run a tool, converting any failure into a readable result."""
        func = TOOL_FUNCTIONS.get(name)
        if func is None:
            return f"Error: no tool named '{name}' exists."
        try:
            return str(func(**args))
        except Exception as exc:
            return f"Error running {name}: {exc}"