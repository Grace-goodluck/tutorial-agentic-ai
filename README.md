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
config.py Central settings and API key loading
providers/
base.py Abstract contract every provider must satisfy
gemini.py Gemini implementation
tools/
registry.py Tool functions and the schemas the model reads
agent.py The reason-act loop
main.py Terminal interface


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

## Tools

| Tool | Purpose |
|------|---------|
| `get_current_time` | Returns the current date and time, which an LLM cannot know |
| `calculate` | Evaluates arithmetic, which LLMs approximate rather than compute |

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


## Possible extensions

- Tools that call external APIs (weather, search, file access)
- Persistent conversation memory across sessions
- A web interface in place of the terminal loop
- A second provider implementation to exercise the abstraction
- Structured logging and token-usage tracking

## Author

Grace Ihuoma Nwakama - TechByGrace