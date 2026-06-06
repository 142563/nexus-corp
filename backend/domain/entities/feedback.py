# domain/entities/feedback.py
# Entidad Feedback — retroalimentación de decisiones para mejorar las reglas.
# Capa: Domain.
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Feedback:
    id: Optional[int]
    decision_id: int
    rule_id: int
    rating: int               # 1 a 5
    was_useful: bool
    real_outcome: str
    observations: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_negative(self) -> bool:
        return self.rating <= 2 or not self.was_useful
