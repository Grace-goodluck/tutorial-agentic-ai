"""Terminal interface for the agent."""

from .agent import Agent


def main() -> None:
    """Run an interactive chat loop until the user exits."""
    print("Agentic AI — type 'quit' to exit.\n")

    agent = Agent(verbose=True)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        try:
            answer = agent.run(user_input)
            print(f"\nAgent: {answer}\n")
        except Exception as exc:
            print(f"\nSomething went wrong: {exc}\n")


if __name__ == "__main__":
    main()