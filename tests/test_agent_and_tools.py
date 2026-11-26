from datetime import date, timedelta
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import init_db
from app.tools import register_study_session, list_pending_reviews, complete_review
from app.main import app


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Cria um banco SQLite temporário e isolado para cada teste."""
    test_db = str(tmp_path / "test_study.db")
    monkeypatch.setattr(settings, "database_path", test_db)
    init_db(test_db)
    yield


def test_register_and_list_study_session():
    created = register_study_session(
        subject="Psicologia Cognitiva",
        topic="Memória de Trabalho",
        difficulty="dificil",
    )

    assert created["id"] == 1
    assert created["subject"] == "Psicologia Cognitiva"
    assert created["next_review_at"] == (date.today() + timedelta(days=1)).isoformat()

    pending = list_pending_reviews()
    assert len(pending) == 1
    assert pending[0]["topic"] == "Memória de Trabalho"


def test_complete_review_updates_status():
    created = register_study_session(
        subject="Neuropsicologia",
        topic="Funções Executivas",
        difficulty="facil",
    )
    result = complete_review(created["id"])

    assert result["updated"] is True
    assert list_pending_reviews() == []


def test_chat_endpoint_with_mocked_agent():
    mocked_response = {
        "reply": "Sessão registrada com sucesso!",
        "tools_called": ["register_study_session"],
    }

    with patch("app.main.run_study_agent", new=AsyncMock(return_value=mocked_response)):
        with TestClient(app) as client:
            response = client.post(
                "/agent/chat",
                json={"message": "Estudei Psicologia Social hoje e achei fácil."},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Sessão registrada com sucesso!"
    assert data["tools_called"] == ["register_study_session"]