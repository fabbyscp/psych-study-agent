from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.database import init_db
from app.schemas import AgentRequest, AgentResponse
from app.agent import run_study_agent
from app.tools import list_pending_reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="MindStudy Agent API",
    description="Agente de IA com Tool Calling para organização de estudos e revisão espaçada em Psicologia.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "ok", "service": "MindStudy Agent"}


@app.post("/agent/chat", response_model=AgentResponse, tags=["Agente IA"])
async def chat_with_agent(payload: AgentRequest):
    try:
        result = await run_study_agent(payload.message)
        return AgentResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro ao processar requisição no agente: {exc}") from exc


@app.get("/reviews/pending", tags=["Revisões"])
async def get_pending_reviews(subject: str | None = None):
    return {"pending_reviews": list_pending_reviews(subject=subject)}