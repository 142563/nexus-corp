# application/dtos/feedback_dto.py
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class FeedbackCreateDTO(BaseModel):
    decision_id: int
    rule_id: int
    rating: int
    was_useful: bool
    real_outcome: str
    observations: str = ""

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return v


class FeedbackResponseDTO(BaseModel):
    id: int
    decision_id: int
    rule_id: int
    rating: int
    was_useful: bool
    real_outcome: str
    observations: str
    created_at: datetime

    model_config = {"from_attributes": True}
