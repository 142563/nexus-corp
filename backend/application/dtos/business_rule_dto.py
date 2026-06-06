# application/dtos/business_rule_dto.py
from pydantic import BaseModel, field_validator
from typing import Any, List, Optional
from datetime import datetime
from backend.domain.entities.business_rule import RuleStatus


class RuleConditionDTO(BaseModel):
    field: str
    operator: str
    value: Any

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid = ("eq", "ne", "gt", "gte", "lt", "lte", "in", "contains")
        if v not in valid:
            raise ValueError(f"Operador inválido '{v}'. Válidos: {valid}")
        return v


class BusinessRuleCreateDTO(BaseModel):
    name: str
    description: str
    conditions: List[RuleConditionDTO]
    suggested_action: str
    priority: int
    area_id: int
    expert_id: int
    confidence_level: float = 0.80
    user_explanation: str = ""


class BusinessRuleUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[List[RuleConditionDTO]] = None
    suggested_action: Optional[str] = None
    priority: Optional[int] = None
    confidence_level: Optional[float] = None
    user_explanation: Optional[str] = None


class RuleStatusUpdateDTO(BaseModel):
    status: RuleStatus


class BusinessRuleResponseDTO(BaseModel):
    id: int
    name: str
    description: str
    conditions: List[RuleConditionDTO]
    suggested_action: str
    priority: int
    area_id: int
    expert_id: int
    status: RuleStatus
    confidence_level: float
    user_explanation: str
    created_at: datetime
    last_reviewed_at: Optional[datetime]

    model_config = {"from_attributes": True}
