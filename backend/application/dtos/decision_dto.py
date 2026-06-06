# application/dtos/decision_dto.py
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class EvaluateSituationDTO(BaseModel):
    input_data: Dict[str, Any]
    request_type: str = "logistica"


class ActivatedRuleDTO(BaseModel):
    rule_id: int
    rule_name: str
    priority: int
    confidence: float
    suggested_action: str


class DecisionResponseDTO(BaseModel):
    request_id: int
    recommendation_id: int
    activated_rules: List[ActivatedRuleDTO]
    suggested_action: str
    confidence: float
    explanation: str
    estimated_risk: str
    requested_at: datetime


class RecordDecisionDTO(BaseModel):
    outcome: str         # aceptada, rechazada, parcialmente_aceptada
    justification: str


class WhatIfScenarioDTO(BaseModel):
    name: str
    input_data: Dict[str, Any]


class WhatIfCompareDTO(BaseModel):
    scenarios: List[WhatIfScenarioDTO]
