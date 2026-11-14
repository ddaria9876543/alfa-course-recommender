
from typing import Literal

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    user_id: int = Field(gt=0)
    goal: str = Field(min_length=1)
    industry: str | None = None

    # Старый параметр — один формат
    preferred_format: Literal[
        "article", "document", "course"
    ] | None = None

    # Новый параметр — несколько форматов
    preferred_formats: list[
        Literal["article", "document", "course"]
    ] | None = None

    business_stage: Literal["planning", "running"] | None = None
    experience: Literal["beginner", "experienced"] | None = None
class RecommendationItem(BaseModel):
    material_id: str
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
    material_id: str
    feedback_type: Literal[
        "already_know",
        "too_hard",
        "irrelevant",
    ]
