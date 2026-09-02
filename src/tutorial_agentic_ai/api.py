"""HTTP interface for the agent."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import config
from .agent import Agent

logger = logging.getLogger(__name__)

config.configure_logging()

app = FastAPI(
    title="Agentic AI",
    description="An AI agent with tool use, exposed over HTTP.",
)

# One shared agent. See README for the limitation this implies.
agent = Agent(verbose=True)
agent.load_history()


class ChatRequest(BaseModel):
    """What the client sends."""
    message: str


class ChatResponse(BaseModel):
    """What the server returns."""
    reply: str


@app.get("/health")
def health() -> dict:
    """Confirm the service is running."""
    return {"status": "ok", "model": config.MODEL_NAME}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the agent and return its reply."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        reply = agent.run(request.message)
    except Exception as exc:
        logger.exception("agent failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    agent.save_history()
    return ChatResponse(reply=reply)


@app.post("/clear")
def clear() -> dict:
    """Forget the conversation."""
    agent.clear_history()
    return {"status": "cleared"}