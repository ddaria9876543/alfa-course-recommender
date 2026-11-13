
from typing import Literal

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    user_id: int = Field(gt=0)
    goal: str = Field(min_length=1)


class RecommendationItem(BaseModel):
    material_id: int
    title: str
    material_type: str
    url: str | None = None
    score: float = Field(ge=0, le=1)
    reason_factors: list[str]
    explanation: str
    step: int


class RecommendationResponse(BaseModel):
    route_id: str
    user_id: int
    goal: str
    recommendations: list[RecommendationItem]


class FeedbackRequest(BaseModel):
    route_id: str
    class FeedbackRequest(BaseModel):
        route_id: str
        material_id: str
        feedback_type: Literal["already_know", "too_hard", "irrelevant"]
    feedback_type: Literal[
        "already_know",
        "too_hard",
        "irrelevant"
    ]