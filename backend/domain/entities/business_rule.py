# domain/entities/business_rule.py
# Entidad BusinessRule y RuleCondition — núcleo del motor de conocimiento.
# Capa: Domain. Contiene las reglas de negocio extraídas de los expertos.
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional
from datetime import datetime


class RuleStatus(str, Enum):
    PENDING = "pendiente"
    ACTIVE = "activa"
    INACTIVE = "inactiva"
    IN_REVIEW = "en_revision"
    REJECTED = "rechazada"


@dataclass
class RuleCondition:
    """Condición individual de una regla de negocio."""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, contains
    value: Any

    def to_dict(self) -> dict:
        return {"field": self.field, "operator": self.operator, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "RuleCondition":
        return cls(field=data["field"], operator=data["operator"], value=data["value"])


@dataclass
class BusinessRule:
    id: Optional[int]
    name: str
    description: str
    conditions: List[RuleCondition]
    suggested_action: str
    priority: int
    area_id: int
    expert_id: int
    status: RuleStatus = RuleStatus.PENDING
    confidence_level: float = 0.80
    user_explanation: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_reviewed_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.status == RuleStatus.ACTIVE

    def activate(self) -> None:
        if self.status != RuleStatus.PENDING:
            raise ValueError(f"Solo se pueden activar reglas en estado pendiente. Estado actual: {self.status}")
        self.status = RuleStatus.ACTIVE
        self.last_reviewed_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.status = RuleStatus.INACTIVE
        self.last_reviewed_at = datetime.utcnow()

    def mark_for_review(self) -> None:
        self.status = RuleStatus.IN_REVIEW
        self.last_reviewed_at = datetime.utcnow()

    def conditions_as_dict_list(self) -> List[dict]:
        return [c.to_dict() for c in self.conditions]
