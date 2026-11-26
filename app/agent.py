from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.config import settings
from app.tools import register_study_session, list_pending_reviews, complete_review

SYSTEM_INSTRUCTION = """
Você é o MindStudy Agent, um assistente acadêmico especializado em organizar sessões de estudo
e revisões espaçadas para estudantes de Psicologia.

Regras de atuação:
1. Sempre utilize as ferramentas disponíveis quando o usuário pedir para registrar um estudo,
   consultar revisões pendentes ou marcar uma revisão como concluída.
2. Nunca invente datas ou registros que não vieram das ferramentas.
3. Ao registrar um estudo, se o usuário não informar a dificuldade explicitamente, infira pelo
   contexto ('facil', 'medio' ou 'dificil') ou adote 'medio'.
4. Responda sempre em português, de forma clara, objetiva e encorajadora.
5. Mantenha o foco estritamente acadêmico e organizacional (não realize aconselhamento psicológico).
"""

AVAILABLE_TOOLS = [
    register_study_session,
    list_pending_reviews,
    complete_review,
]

FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
]


async def run_study_agent(user_message: str) -> dict:
    """Executa o agente de estudos com chamada automática de ferramentas e fallback entre modelos."""
    client = genai.Client(api_key=settings.gemini_api_key)
    last_error: Exception | None = None

    for model_name in FALLBACK_MODELS:
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=AVAILABLE_TOOLS,
                    temperature=0.2,
                ),
            )

            tools_called: list[str] = []
            if response.automatic_function_calling_history:
                for content in response.automatic_function_calling_history:
                    if content.parts:
                        for part in content.parts:
                            if part.function_call and part.function_call.name:
                                tools_called.append(part.function_call.name)

            return {
                "reply": response.text or "Não foi possível gerar uma resposta no momento.",
                "tools_called": tools_called,
            }
        except APIError as exc:
            last_error = exc
            if exc.code in (404, 429, 503):
                continue
            raise

    raise RuntimeError(f"Todos os modelos estão temporariamente indisponíveis: {last_error}")