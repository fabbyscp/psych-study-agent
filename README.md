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