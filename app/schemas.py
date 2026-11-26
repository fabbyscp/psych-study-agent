from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=3,
        description="Mensagem em linguagem natural para o agente de estudos",
        examples=["Estudei Condicionamento Operante em Análise do Comportamento hoje e achei difícil."],
    )


class AgentResponse(BaseModel):
    reply: str
    tools_called: list[str]