"""The agent control loop."""

from google.genai import types

from . import config
from .providers.gemini import GeminiProvider
from .tools.registry import TOOL_FUNCTIONS, TOOL_SCHEMAS


class Agent:
    """Runs the reason-act loop: model decides, tools execute, repeat."""

    def __init__(self, verbose: bool = True) -> None:
        self.provider = GeminiProvider()
        self.verbose = verbose
        self.messages: list = []

    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"  [agent] {message}")

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