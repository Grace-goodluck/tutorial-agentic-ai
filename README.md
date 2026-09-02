# Agentic AI

A from-scratch AI agent in Python. The agent uses an LLM as a reasoning
engine, decides when to call tools, executes them, and feeds the results
back into its own context until it can answer.

Built without an agent framework, so every part of the control loop is
explicit and inspectable.

## What makes this an agent, not a chatbot

A chatbot maps text to text. This application runs a reason-act loop:

1. The user's request is added to the conversation
2. The conversation and the tool descriptions are sent to the model
3. The model either answers directly or requests a tool call
4. If a tool is requested, it runs and its result is appended
5. Repeat until the model answers, or until the iteration limit is hit

The model never executes anything. It emits a structured request; the
application decides whether and how to act on it.

## Architecture
src/tutorial_agentic_ai/
    config.py           Central settings, API key loading, logging setup
    providers/
        base.py         Abstract contract every provider must satisfy
        gemini.py       Gemini implementation with retry logic
    tools/
        registry.py     Tool functions and the schemas the model reads
    agent.py            The reason-act loop and conversation persistence
    main.py             Terminal interface

data/
    history.json        Saved conversation (gitignored)

tests/
    test_tools.py       Unit tests for tools and registry consistency


### Design decisions

**Provider abstraction.** `agent.py` depends on the `ModelProvider`
interface, never on a vendor SDK. Supporting a different model means
adding one file, not editing agent logic.

**Automatic function calling disabled.** The Gemini SDK can execute
tools transparently. That is switched off deliberately so the control
loop lives in this codebase and can be reasoned about and modified.

**Iteration limit.** `MAX_ITERATIONS` in `config.py` caps how many tool
calls a single request may trigger, preventing runaway loops and
uncontrolled API spend.

**Tools fail as data, not exceptions.** A failing tool returns an error
string the model can read and respond to, so a bad tool call never
crashes the agent.

**Sandboxed evaluation.** The calculator whitelists digits and basic
operators before evaluating, since passing model output to `eval`
unchecked is an injection risk.

**Retry with exponential backoff.** Transient server errors (5xx) are
retried up to three times with a doubling delay. Client errors (4xx) are
not retried, since a bad key or wrong model name will fail identically on
every attempt.

**Structured logging.** The agent logs through Python's `logging` module
rather than printing, so verbosity is controlled by a single config value
and diagnostic output stays separate from user-facing text.

**Provider-neutral persistence.** Conversation history is stored as plain
JSON rather than pickled SDK objects, so the saved format does not depend
on which model provider produced it. Only message text is kept — stale
tool results from a previous session would mislead the model rather than
help it.

## Tools

| Tool | Purpose |
|------|---------|
| `get_current_time` | Returns the current date and time, which an LLM cannot know |
| `calculate` | Evaluates arithmetic, which LLMs approximate rather than compute |
| `get_weather` | Fetches live conditions for any city via Open-Meteo, with geocoding |

## Setup

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file in the project root:


Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).
`.env` is gitignored and must never be committed.

[agent] iteration 1: asking the model
  [agent] model requested tool: get_current_time({})
  [agent] tool returned: Friday, 28 August 2026 at 14:46
  [agent] model requested tool: calculate({'expression': '0.15 * 4820'})
  [agent] tool returned: 723.0
  [agent] iteration 2: asking the model
  [agent] model returned a final answer

Agent: The current time is **2:46 PM** on **Friday, August 28, 2026** (14:46 UTC).

15% of 4,820 is **723**.

You: how are you
  [agent] iteration 1: asking the model
  [agent] model returned a final answer

Agent: I'm doing great, thank you for asking! How can I help you today?

## Running 

```bash
uv run python -m tutorial_agentic_ai.main
```
Conversation history persists between sessions. Type `/clear` to forget it. 

## Tests
'''bash
uv run pytest
'''

Covers the tool functions, the sandbox guard against code injection, and consistency between tool schemas and their implementations - a mismatch there would leave a tool invisible to the model.
   
## Possible extensions

- Tools that call external APIs (weather, search, file access)
- Persistent conversation memory across sessions
- A web interface in place of the terminal loop
- A second provider implementation to exercise the abstraction
- Structured logging and token-usage tracking

## Web interface

The agent is also exposed over HTTP. Start the server:

```bash
uv run uvicorn tutorial_agentic_ai.api:app --reload
```

Then open http://127.0.0.1:8000 for the chat page, or
http://127.0.0.1:8000/docs for the generated API documentation.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Chat page |
| `/health` | GET | Liveness check |
| `/chat` | POST | Send a message, receive the agent's reply |
| `/clear` | POST | Forget the conversation |

### Known limitations

**Single shared agent.** The server holds one agent instance, so all
visitors share one conversation. Correct for a local demo; a deployed
version would need per-session state.

**No Markdown rendering.** Replies are inserted with `textContent`
rather than `innerHTML`, so model output containing HTML cannot execute
in the browser. The tradeoff is that Markdown formatting appears as
literal characters.

**Not deployment-ready.** The API key is read from the server's
environment, so a public deployment would let any visitor spend the
owner's quota. Authentication or per-user keys would be required first.

## Author

Grace Ihuoma Nwakama - TechByGrace