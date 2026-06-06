# application/use_cases/evaluate_situation.py
# Caso de uso principal: evalúa una situación logística contra las reglas activas.
# Capa: Application. Orquesta el motor de reglas y persiste el resultado.
from datetime import datetime
from typing import Any, Dict

from backend.domain.entities.decision import DecisionRequest, DecisionRecommendation
from backend.domain.repositories import IBusinessRuleRepository, IDecisionRepository
from backend.domain.rule_engine import RuleEngine
from backend.application.dtos.decision_dto import DecisionResponseDTO, ActivatedRuleDTO, EvaluateSituationDTO


class EvaluateSituationUseCase:
    def __init__(
        self,
        rule_repo: IBusinessRuleRepository,
        decision_repo: IDecisionRepository,
        rule_engine: RuleEngine,
    ):
        self._rule_repo = rule_repo
        self._decision_repo = decision_repo
        self._engine = rule_engine

    def execute(self, dto: EvaluateSituationDTO, user_id: int) -> DecisionResponseDTO:
        request = DecisionRequest(
            id=None,
            user_id=user_id,
            input_data=dto.input_data,
            request_type=dto.request_type,
            requested_at=datetime.utcnow(),
        )
        saved_request = self._decision_repo.save_request(request)

        active_rules = self._rule_repo.get_active_rules()
        matched = self._engine.evaluate(active_rules, dto.input_data)

        activated_dtos = [
            ActivatedRuleDTO(
                rule_id=r.id,
                rule_name=r.name,
                priority=r.priority,
                confidence=r.confidence_level,
                suggested_action=r.suggested_action,
            )
            for r in matched
        ]

        top_action = matched[0].suggested_action if matched else "Sin recomendación — revisar parámetros."
        confidence = self._engine.calculate_aggregate_confidence(matched)
        explanation = self._engine.build_explanation(matched, dto.input_data)
        risk = self._engine.estimate_risk(matched)

        recommendation = DecisionRecommendation(
            id=None,
            request_id=saved_request.id,
            activated_rules=[
                {"rule_id": r.id, "rule_name": r.name, "priority": r.priority, "confidence": r.confidence_level}
                for r in matched
            ],
            suggested_action=top_action,
            confidence=confidence,
            explanation=explanation,
            estimated_risk=risk,
        )
        saved_rec = self._decision_repo.save_recommendation(recommendation)

        return DecisionResponseDTO(
            request_id=saved_request.id,
            recommendation_id=saved_rec.id,
            activated_rules=activated_dtos,
            suggested_action=top_action,
            confidence=confidence,
            explanation=explanation,
            estimated_risk=risk,
            requested_at=saved_request.requested_at,
        )
