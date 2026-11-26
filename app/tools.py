from datetime import date, timedelta
from app.database import get_connection


REVIEW_INTERVALS_DAYS = {
    "facil": 7,
    "medio": 3,
    "dificil": 1,
}


def register_study_session(subject: str, topic: str, difficulty: str) -> dict:
    """Registra uma nova sessão de estudo de Psicologia e calcula a próxima data de revisão espaçada.

    Args:
        subject: Nome da disciplina (ex: Psicologia Cognitiva, Neuropsicologia, Análise do Comportamento).
        topic: Tópico específico estudado (ex: Condicionamento Operante, Memória de Trabalho).
        difficulty: Nível de dificuldade percebida ('facil', 'medio' ou 'dificil').

    Returns:
        Dicionário com os dados registrados e a data agendada para revisão.
    """
    normalized_diff = difficulty.strip().lower()
    if normalized_diff not in REVIEW_INTERVALS_DAYS:
        normalized_diff = "medio"

    today = date.today()
    days_until_review = REVIEW_INTERVALS_DAYS[normalized_diff]
    next_review = today + timedelta(days=days_until_review)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO study_sessions (subject, topic, difficulty, studied_at, next_review_at, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (subject.strip(), topic.strip(), normalized_diff, today.isoformat(), next_review.isoformat()),
        )
        conn.commit()
        session_id = cursor.lastrowid

    return {
        "id": session_id,
        "subject": subject.strip(),
        "topic": topic.strip(),
        "difficulty": normalized_diff,
        "studied_at": today.isoformat(),
        "next_review_at": next_review.isoformat(),
        "interval_days": days_until_review,
    }


def list_pending_reviews(subject: str | None = None) -> list[dict]:
    """Lista todas as revisões de estudo pendentes no banco de dados, opcionalmente filtradas por disciplina.

    Args:
        subject: Nome opcional da disciplina para filtrar os resultados.

    Returns:
        Lista de dicionários contendo as sessões pendentes ordenadas pela data de revisão.
    """
    with get_connection() as conn:
        if subject:
            rows = conn.execute(
                """
                SELECT id, subject, topic, difficulty, studied_at, next_review_at, status
                FROM study_sessions
                WHERE status = 'pending' AND LOWER(subject) LIKE ?
                ORDER BY next_review_at ASC
                """,
                (f"%{subject.strip().lower()}%",),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, subject, topic, difficulty, studied_at, next_review_at, status
                FROM study_sessions
                WHERE status = 'pending'
                ORDER BY next_review_at ASC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def complete_review(session_id: int) -> dict:
    """Marca uma revisão pendente como concluída pelo seu ID.

    Args:
        session_id: Identificador numérico (ID) da sessão de estudo a ser concluída.

    Returns:
        Dicionário informando se a atualização foi realizada com sucesso.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE study_sessions
            SET status = 'completed'
            WHERE id = ? AND status = 'pending'
            """,
            (session_id,),
        )
        conn.commit()

    if cursor.rowcount == 0:
        return {"updated": False, "message": f"Nenhuma revisão pendente encontrada com ID {session_id}."}

    return {"updated": True, "session_id": session_id, "status": "completed"}