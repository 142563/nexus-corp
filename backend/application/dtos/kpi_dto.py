# application/dtos/kpi_dto.py
from pydantic import BaseModel
from typing import List


class KPIDashboardDTO(BaseModel):
    total_decisions: int
    acceptance_rate: float        # porcentaje 0–100
    average_response_time_ms: float
    active_rules_count: int
    average_feedback_rating: float
    decisions_last_7_days: int
    rules_in_review: int


class TrendPointDTO(BaseModel):
    date: str
    decisions: int
    accepted: int
    avg_confidence: float


class KPITrendsDTO(BaseModel):
    trends: List[TrendPointDTO]
