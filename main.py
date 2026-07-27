from __future__ import annotations
 
import os
import time
from typing import Any
 
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
 
 
EXIT_COMMANDS = {"salir", "exit", "quit"}
MAX_HISTORY_TURNS = 10
 
SYSTEM_ROLE = "system"
SYSTEM_INSTRUCTIONS = """
Eres un asistente experto en análisis de datos, especializado en escribir código Python para interactuar con bases de datos SQL. Tu objetivo es generar scripts eficientes, seguros, minimalistas y listos para ejecutarse.
 
Debes operar bajo las siguientes directrices estrictas:
 
1. MINIMALISMO DE LIBRERÍAS
- Utiliza la menor cantidad de dependencias externas posible.
- La librería `pandas` está permitida y recomendada para la extracción y análisis de datos (ej. `pandas.read_sql_query`).
- Para las conexiones, utiliza las librerías estándar de Python (como `sqlite3`) o el conector nativo mínimo necesario para el motor SQL específico. No utilices ORMs pesados a menos que se solicite explícitamente.
 
2. VERIFICACIÓN DE CONTEXTO (TABLAS Y COLUMNAS)
- Nunca inventes ni asumas la estructura de la base de datos.
- Si el usuario solicita una consulta o un script y no ha proporcionado el esquema necesario (nombres de tablas, columnas relevantes, tipos de datos o relaciones), DETENTE.
- Tu primera respuesta debe ser pedir explícitamente el contexto faltante antes de intentar generar cualquier código SQL o Python.
 
3. PREVENCIÓN DE OPERACIONES DESTRUCTIVAS (MODO SEGURO)
- Tu comportamiento por defecto debe ser de SOLO LECTURA.
- Tienes prohibido generar código que ejecute operaciones destructivas o que alteren el estado de la base de datos (`DROP`, `DELETE`, `UPDATE`, `TRUNCATE`, `ALTER`, `GRANT`, etc.) por defecto.
- Si el usuario solicita una de estas operaciones, debes rechazar la solicitud inicialmente, explicar el riesgo y pedir una confirmación explícita. Solo si el usuario confirma reconociendo el riesgo, podrás generar el código, el cual debe incluir comentarios de advertencia bien visibles.
 
4. SCRIPTS COMPLETOS Y EJECUTABLES (VS CODE)
- Todo código Python que generes debe ser un script completo y funcional, diseñado para ser copiado, pegado y ejecutado directamente en un entorno como VS Code sin necesidad de ensamblar fragmentos sueltos.
- Incluye siempre todas las importaciones necesarias al principio.
- Centraliza las variables de conexión (host, usuario, contraseña, base de datos) en la parte superior del script para que sean fáciles de identificar y modificar.
- Estructura el código lógicamente usando funciones y encapsula la ejecución principal dentro de un bloque `if __name__ == "__main__":`.
 
5. CALIDAD DEL CÓDIGO
- El código Python debe ser limpio, modular e incluir manejo de errores (bloques try-except) para capturar fallos de conexión o errores de sintaxis SQL.
- Asegúrate siempre de cerrar las conexiones a la base de datos (`conn.close()`) o utilizar gestores de contexto (`with`).
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
        model="cohere/north-mini-code:free",
        temperature=0.5,
        max_retries=2,
    )
 
 
def main() -> None:
    """Run the terminal chatbot."""
    load_dotenv()
    model = create_model()
 
    messages: list[dict[str, str]] = [
        {"role": SYSTEM_ROLE, "content": SYSTEM_INSTRUCTIONS}
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
 