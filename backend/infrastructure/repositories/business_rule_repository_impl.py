# infrastructure/repositories/business_rule_repository_impl.py
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.domain.entities.business_rule import BusinessRule, RuleCondition, RuleStatus
from backend.domain.repositories.business_rule_repository import IBusinessRuleRepository
from backend.infrastructure.database.models import BusinessRuleModel


class BusinessRuleRepositoryImpl(IBusinessRuleRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, rule_id: int) -> Optional[BusinessRule]:
        m = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.id == rule_id).first()
        return self._to_entity(m) if m else None

    def get_all(self) -> List[BusinessRule]:
        return [self._to_entity(m) for m in self._db.query(BusinessRuleModel).all()]

    def get_active_rules(self) -> List[BusinessRule]:
        rows = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.status == "activa").all()
        return [self._to_entity(m) for m in rows]

    def get_by_area(self, area_id: int) -> List[BusinessRule]:
        rows = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.area_id == area_id).all()
        return [self._to_entity(m) for m in rows]

    def get_by_status(self, status: RuleStatus) -> List[BusinessRule]:
        rows = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.status == status.value).all()
        return [self._to_entity(m) for m in rows]

    def save(self, rule: BusinessRule) -> BusinessRule:
        m = BusinessRuleModel(
            name=rule.name, description=rule.description,
            conditions=rule.conditions_as_dict_list(),
            suggested_action=rule.suggested_action, priority=rule.priority,
            area_id=rule.area_id, expert_id=rule.expert_id,
            status=rule.status.value, confidence_level=rule.confidence_level,
            user_explanation=rule.user_explanation, created_at=rule.created_at,
            last_reviewed_at=rule.last_reviewed_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def update(self, rule: BusinessRule) -> BusinessRule:
        m = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.id == rule.id).first()
        if not m:
            raise ValueError(f"Regla {rule.id} no encontrada.")
        m.name = rule.name
        m.description = rule.description
        m.conditions = rule.conditions_as_dict_list()
        m.suggested_action = rule.suggested_action
        m.priority = rule.priority
        m.status = rule.status.value
        m.confidence_level = rule.confidence_level
        m.user_explanation = rule.user_explanation
        m.last_reviewed_at = rule.last_reviewed_at
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def delete(self, rule_id: int) -> None:
        m = self._db.query(BusinessRuleModel).filter(BusinessRuleModel.id == rule_id).first()
        if m:
            self._db.delete(m)
            self._db.commit()

    @staticmethod
    def _to_entity(m: BusinessRuleModel) -> BusinessRule:
        conditions = [RuleCondition.from_dict(c) for c in (m.conditions or [])]
        return BusinessRule(
            id=m.id, name=m.name, description=m.description,
            conditions=conditions, suggested_action=m.suggested_action,
            priority=m.priority, area_id=m.area_id, expert_id=m.expert_id,
            status=RuleStatus(m.status), confidence_level=m.confidence_level,
            user_explanation=m.user_explanation, created_at=m.created_at,
            last_reviewed_at=m.last_reviewed_at,
        )
