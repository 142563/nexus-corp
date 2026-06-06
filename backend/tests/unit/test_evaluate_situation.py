# tests/unit/test_evaluate_situation.py
# Pruebas unitarias del caso de uso EvaluateSituationUseCase con repositorios en memoria.
from datetime import datetime
from unittest.mock import MagicMock
import pytest

from backend.domain.entities.business_rule import BusinessRule, RuleCondition, RuleStatus
from backend.domain.entities.decision import DecisionRequest, DecisionRecommendation
from backend.domain.rule_engine import RuleEngine
from backend.application.use_cases.evaluate_situation import EvaluateSituationUseCase
from backend.application.dtos.decision_dto import EvaluateSituationDTO


def _make_active_rule(rule_id, conditions, priority=5, confidence=0.85):
    r = BusinessRule(
        id=rule_id, name=f"RN-{rule_id:03d}", description="Test",
        conditions=conditions, suggested_action=f"Acción {rule_id}",
        priority=priority, area_id=1, expert_id=1,
        status=RuleStatus.ACTIVE, confidence_level=confidence,
    )
    return r


def _mock_repos(active_rules):
    rule_repo = MagicMock()
    rule_repo.get_active_rules.return_value = active_rules

    decision_repo = MagicMock()
    counter = {"req": 0, "rec": 0}

    def save_request(req):
        counter["req"] += 1
        req.id = counter["req"]
        return req

    def save_recommendation(rec):
        counter["rec"] += 1
        rec.id = counter["rec"]
        return rec

    decision_repo.save_request.side_effect = save_request
    decision_repo.save_recommendation.side_effect = save_recommendation
    return rule_repo, decision_repo


class TestEvaluateSituationUseCase:
    def test_single_rule_activated(self):
        rule = _make_active_rule(1, [RuleCondition("order_priority", "eq", "alta")])
        rule_repo, decision_repo = _mock_repos([rule])
        uc = EvaluateSituationUseCase(rule_repo, decision_repo, RuleEngine())
        dto = EvaluateSituationDTO(input_data={"order_priority": "alta"})
        result = uc.execute(dto, user_id=1)
        assert len(result.activated_rules) == 1
        assert result.activated_rules[0].rule_id == 1
        assert result.confidence > 0

    def test_no_rules_activated(self):
        rule = _make_active_rule(1, [RuleCondition("order_priority", "eq", "alta")])
        rule_repo, decision_repo = _mock_repos([rule])
        uc = EvaluateSituationUseCase(rule_repo, decision_repo, RuleEngine())
        dto = EvaluateSituationDTO(input_data={"order_priority": "baja"})
        result = uc.execute(dto, user_id=1)
        assert result.activated_rules == []
        assert result.confidence == 0.0
        assert "Ninguna" in result.explanation

    def test_multiple_rules_sorted_by_priority(self):
        r1 = _make_active_rule(1, [RuleCondition("x", "eq", 1)], priority=3)
        r2 = _make_active_rule(2, [RuleCondition("x", "eq", 1)], priority=9)
        rule_repo, decision_repo = _mock_repos([r1, r2])
        uc = EvaluateSituationUseCase(rule_repo, decision_repo, RuleEngine())
        dto = EvaluateSituationDTO(input_data={"x": 1})
        result = uc.execute(dto, user_id=1)
        assert len(result.activated_rules) == 2
        assert result.activated_rules[0].priority == 9

    def test_persists_request_and_recommendation(self):
        rule = _make_active_rule(1, [RuleCondition("a", "eq", 1)])
        rule_repo, decision_repo = _mock_repos([rule])
        uc = EvaluateSituationUseCase(rule_repo, decision_repo, RuleEngine())
        uc.execute(EvaluateSituationDTO(input_data={"a": 1}), user_id=5)
        decision_repo.save_request.assert_called_once()
        decision_repo.save_recommendation.assert_called_once()
