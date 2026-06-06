# domain/entities/decision.py
# Entidades del ciclo de decisión: solicitud, recomendación y registro.
# Capa: Domain.
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class DecisionRequest:
    id: Optional[int]
    user_id: int
    input_data: Dict[str, Any]
    request_type: str
    requested_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DecisionRecommendation:
    id: Optional[int]
    request_id: int
    activated_rules: List[Dict]   # lista de {rule_id, rule_name, priority, confidence}
    suggested_action: str
    confidence: float
    explanation: str
    estimated_risk: str           # bajo, medio, alto

    def has_recommendations(self) -> bool:
        return len(self.activated_rules) > 0


@dataclass
class DecisionRecord:
    id: Optional[int]
    recommendation_id: int
    user_id: int
    outcome: str                  # aceptada, rechazada, parcialmente_aceptada
    justification: str
    decided_at: datetime = field(default_factory=datetime.utcnow)
