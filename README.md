# MindStudy Agent API

[Português](#português) | [English](#english)

---

## Português

API REST de um **Agente de IA com Orquestração e Tool Calling** construída com **FastAPI**, **Google GenAI SDK** e **SQLite** para organização acadêmica e agendamento automático de revisões espaçadas em Psicologia.

### Arquitetura e Decisões Técnicas

- **Agentic Workflow (Tool Calling):** O modelo interpreta intenções em linguagem natural e decide autonomamente quais funções Python acionar (`register_study_session`, `list_pending_reviews`, `complete_review`), retornando a resposta fundamentada nos dados persistidos e a lista de ferramentas acionadas (`tools_called`).
- **Resiliência e Fallback entre Modelos:** O orquestrador implementa fallback automático entre modelos Gemini (`gemini-3.8-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash-lite`) em caso de indisponibilidade temporária (`503`) ou limite de requisições (`429`).
- **Persistência e Isolamento:** Banco relacional leve com **SQLite**, validado por suíte de testes automatizados com **Pytest** utilizando bancos temporários isolados (`tmp_path`) e mocks assíncronos (`AsyncMock`).

### Estrutura do Projeto

```text
psych-study-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py       # Orquestração do agente Gemini com Tool Calling e fallback
│   ├── config.py      # Configurações via Pydantic Settings (.env)
│   ├── database.py    # Conexão e inicialização da tabela SQLite
│   ├── main.py        # Endpoints FastAPI e ciclo de vida (lifespan)
│   ├── schemas.py     # Contratos de entrada/saída com Pydantic
│   └── tools.py       # Ferramentas Python executadas pelo agente
├── tests/
│   ├── __init__.py
│   └── test_agent_and_tools.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

---

## English

REST API for an **AI Agent with Orchestration and Tool Calling** built with **FastAPI**, **Google GenAI SDK**, and **SQLite** for academic organization and automated spaced-repetition scheduling in Psychology.

### Architecture & Technical Decisions

- **Agentic Workflow (Tool Calling):** The model interprets natural language intents and autonomously decides which Python tools to invoke (`register_study_session`, `list_pending_reviews`, `complete_review`), returning responses grounded in persisted data along with the list of invoked tools (`tools_called`).
- **Resilience & Model Fallback:** The orchestrator implements automatic fallback across Gemini models (`gemini-3.8-flash` -> `gemini-3.7-flash` -> `gemini-3.5-flash-lite`) to handle transient overload (`503`) or rate-limit (`429`) responses.
- **Persistence & Test Isolation:** Lightweight relational storage with **SQLite**, validated by an automated **Pytest** suite using isolated temporary databases (`tmp_path`) and asynchronous mocks (`AsyncMock`).

### Project Structure

- `app/agent.py`: Gemini agent orchestration with Tool Calling and fallback
- `app/config.py`: Configuration via Pydantic Settings (`.env`)
- `app/database.py`: SQLite connection and schema initialization
- `app/main.py`: FastAPI endpoints and lifespan management
- `app/schemas.py`: Pydantic request/response schemas
- `app/tools.py`: Python tools executed by the agent
- `tests/test_agent_and_tools.py`: Automated tests with Pytest

### Running Locally

1. Clone the repository: `git clone https://github.com/fabbyscp/psych-study-agent.git && cd psych-study-agent`
2. Create and activate the virtual environment: `python -m venv venv` and `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`
5. Start the API: `uvicorn app.main:app --reload` (Swagger UI at `http://127.0.0.1:8000/docs`)
6. Run tests: `pytest -v`