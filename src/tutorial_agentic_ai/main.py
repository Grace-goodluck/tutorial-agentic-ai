"""Terminal interface for the agent."""

from . import config
from .agent import Agent

def main() -> None:
    """Run an interactive chat loop until the user exits."""
    config.configure_logging()
    print("Agentic AI — type 'quit' to exit.\n")

    agent = Agent(verbose=True)
    agent.load_history()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            agent.save_history()
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit"}:
            agent.save_history()
            print("Goodbye.")
            break

        if user_input.lower() == "/clear":
            agent.clear_history()
            print("History cleared.\n")
            continue    

        try:
            answer = agent.run(user_input)
            print(f"\nAgent: {answer}\n")
        except Exception as exc:
            print(f"\nSomething went wrong: {exc}\n")


if __name__ == "__main__":
    main()