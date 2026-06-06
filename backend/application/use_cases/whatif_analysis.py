# application/use_cases/whatif_analysis.py
# Análisis What-If: evalúa escenarios hipotéticos sin persistir en el historial real.
# Capa: Application.
from typing import Any, Dict, List

from backend.domain.repositories import IBusinessRuleRepository
from backend.domain.rule_engine import RuleEngine
from backend.application.dtos.decision_dto import WhatIfScenarioDTO, ActivatedRuleDTO


class ScenarioResultDTO:
    def __init__(self, name: str, activated_rules: List[ActivatedRuleDTO],
                 suggested_action: str, confidence: float, risk: str, explanation: str):
        self.name = name
        self.activated_rules = activated_rules
        self.suggested_action = suggested_action
        self.confidence = confidence
        self.risk = risk
        self.explanation = explanation

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "activated_rules": [r.model_dump() for r in self.activated_rules],
            "suggested_action": self.suggested_action,
            "confidence": self.confidence,
            "risk": self.risk,
            "explanation": self.explanation,
        }


class WhatIfAnalysisUseCase:
    def __init__(self, rule_repo: IBusinessRuleRepository, rule_engine: RuleEngine):
        self._repo = rule_repo
        self._engine = rule_engine

    def evaluate_scenario(self, scenario: WhatIfScenarioDTO) -> ScenarioResultDTO:
        active_rules = self._repo.get_active_rules()
        matched = self._engine.evaluate(active_rules, scenario.input_data)
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
        top_action = matched[0].suggested_action if matched else "Sin recomendación."
        return ScenarioResultDTO(
            name=scenario.name,
            activated_rules=activated_dtos,
            suggested_action=top_action,
            confidence=self._engine.calculate_aggregate_confidence(matched),
            risk=self._engine.estimate_risk(matched),
            explanation=self._engine.build_explanation(matched, scenario.input_data),
        )

    def compare_scenarios(self, scenarios: List[WhatIfScenarioDTO]) -> List[dict]:
        return [self.evaluate_scenario(s).to_dict() for s in scenarios]
