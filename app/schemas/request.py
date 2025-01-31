from typing import List

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    id: int
    query: str


class PredictionResponse(BaseModel):
    id: int
    answer: int | None = None
    reasoning: str
    sources: List[str]

class AgentResponse(BaseModel):
    answer: int | None = None
    reasoning: str
