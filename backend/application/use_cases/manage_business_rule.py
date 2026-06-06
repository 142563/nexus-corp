# application/use_cases/manage_business_rule.py
# CRUD de reglas de negocio con validación de transiciones de estado.
# Capa: Application.
from typing import List, Optional
from datetime import datetime

from backend.domain.entities.business_rule import BusinessRule, RuleCondition, RuleStatus
from backend.domain.repositories import IBusinessRuleRepository
from backend.application.dtos.business_rule_dto import (
    BusinessRuleCreateDTO,
    BusinessRuleUpdateDTO,
    BusinessRuleResponseDTO,
)


class ManageBusinessRuleUseCase:
    def __init__(self, rule_repo: IBusinessRuleRepository):
        self._repo = rule_repo

    def create(self, dto: BusinessRuleCreateDTO) -> BusinessRuleResponseDTO:
        conditions = [RuleCondition(field=c.field, operator=c.operator, value=c.value) for c in dto.conditions]
        rule = BusinessRule(
            id=None,
            name=dto.name,
            description=dto.description,
            conditions=conditions,
            suggested_action=dto.suggested_action,
            priority=dto.priority,
            area_id=dto.area_id,
            expert_id=dto.expert_id,
            confidence_level=dto.confidence_level,
            user_explanation=dto.user_explanation,
        )
        saved = self._repo.save(rule)
        return self._to_response(saved)

    def get_all(self) -> List[BusinessRuleResponseDTO]:
        return [self._to_response(r) for r in self._repo.get_all()]

    def get_by_id(self, rule_id: int) -> Optional[BusinessRuleResponseDTO]:
        rule = self._repo.get_by_id(rule_id)
        return self._to_response(rule) if rule else None

    def update(self, rule_id: int, dto: BusinessRuleUpdateDTO) -> BusinessRuleResponseDTO:
        rule = self._repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Regla {rule_id} no encontrada.")
        if dto.name is not None:
            rule.name = dto.name
        if dto.description is not None:
            rule.description = dto.description
        if dto.conditions is not None:
            rule.conditions = [RuleCondition(field=c.field, operator=c.operator, value=c.value) for c in dto.conditions]
        if dto.suggested_action is not None:
            rule.suggested_action = dto.suggested_action
        if dto.priority is not None:
            rule.priority = dto.priority
        if dto.confidence_level is not None:
            rule.confidence_level = dto.confidence_level
        if dto.user_explanation is not None:
            rule.user_explanation = dto.user_explanation
        updated = self._repo.update(rule)
        return self._to_response(updated)

    def change_status(self, rule_id: int, new_status: RuleStatus) -> BusinessRuleResponseDTO:
        rule = self._repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Regla {rule_id} no encontrada.")
        if new_status == RuleStatus.ACTIVE:
            rule.activate()
        elif new_status == RuleStatus.INACTIVE:
            rule.deactivate()
        elif new_status == RuleStatus.IN_REVIEW:
            rule.mark_for_review()
        else:
            rule.status = new_status
            rule.last_reviewed_at = datetime.utcnow()
        updated = self._repo.update(rule)
        return self._to_response(updated)

    def delete(self, rule_id: int) -> None:
        self._repo.delete(rule_id)

    @staticmethod
    def _to_response(rule: BusinessRule) -> BusinessRuleResponseDTO:
        from backend.application.dtos.business_rule_dto import RuleConditionDTO
        return BusinessRuleResponseDTO(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            conditions=[RuleConditionDTO(field=c.field, operator=c.operator, value=c.value) for c in rule.conditions],
            suggested_action=rule.suggested_action,
            priority=rule.priority,
            area_id=rule.area_id,
            expert_id=rule.expert_id,
            status=rule.status,
            confidence_level=rule.confidence_level,
            user_explanation=rule.user_explanation,
            created_at=rule.created_at,
            last_reviewed_at=rule.last_reviewed_at,
        )
