from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


EXIT_COMMANDS = {"salir", "exit", "quit"}
MAX_HISTORY_TURNS = 10

SYSTEM_PROMPT = """

""".strip()


def require_environment_variable(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"No se encontró {name}. "
            "Copia .env.example como .env y agrega tu clave."
        )
    return value


def response_to_text(response: Any) -> str:
    """Convert a LangChain response into plain text."""
    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()

    return str(content).strip()


def trim_history(
    messages: list[dict[str, str]],
    max_turns: int = MAX_HISTORY_TURNS,
) -> list[dict[str, str]]:
    """Keep the system prompt and the most recent chat turns."""
    system_message = messages[:1]
    recent_messages = messages[-(max_turns * 2):]
    return system_message + recent_messages


def create_model() -> ChatOpenRouter:
    """Create the OpenRouter model configured from environment variables."""
    require_environment_variable("OPENROUTER_API_KEY")

    return ChatOpenRouter(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        temperature=0.5,
        max_retries=2,
    )


def main() -> None:
    """Run the terminal chatbot."""
    load_dotenv()
    model = create_model()

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    print(
        "Mi primer Chatbot vía OpenRouter.\n"
        "Escribe 'salir' para terminar.\n"
    )

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("Hasta luego.")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = model.invoke(messages)
            bot_text = response_to_text(response)

            if not bot_text:
                bot_text = "No se recibió contenido del modelo."

            print(f"Bot: {bot_text}\n")
            messages.append({"role": "assistant", "content": bot_text})
            messages = trim_history(messages)

            time.sleep(2)

        except Exception as error:
            print(f"Error al consultar OpenRouter: {error}\n")

            if messages and messages[-1].get("role") == "user":
                messages.pop()


if __name__ == "__main__":
    main()
