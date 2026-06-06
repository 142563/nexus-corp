# tests/unit/test_record_feedback.py
# Verifica que RN-005 se dispara correctamente con el umbral de retroalimentación negativa.
from unittest.mock import MagicMock
from datetime import datetime

from backend.domain.entities.feedback import Feedback
from backend.domain.entities.business_rule import BusinessRule, RuleCondition, RuleStatus
from backend.application.use_cases.record_feedback import RecordFeedbackUseCase, NEGATIVE_THRESHOLD, REVIEW_WINDOW
from backend.application.dtos.feedback_dto import FeedbackCreateDTO


def _active_rule():
    return BusinessRule(
        id=1, name="RN-001", description="Test",
        conditions=[], suggested_action="Acción", priority=5,
        area_id=1, expert_id=1, status=RuleStatus.ACTIVE, confidence_level=0.9,
    )


def _make_negative(n: int):
    return [
        Feedback(id=i, decision_id=1, rule_id=1, rating=1, was_useful=False,
                 real_outcome="malo", observations="", created_at=datetime.utcnow())
        for i in range(n)
    ]


class TestRecordFeedbackUseCase:
    def test_no_trigger_below_threshold(self):
        feedback_repo = MagicMock()
        rule_repo = MagicMock()
        feedback_repo.save.side_effect = lambda f: setattr(f, "id", 1) or f
        feedback_repo.get_recent_negatives_for_rule.return_value = _make_negative(NEGATIVE_THRESHOLD - 1)

        uc = RecordFeedbackUseCase(feedback_repo, rule_repo)
        dto = FeedbackCreateDTO(decision_id=1, rule_id=1, rating=2, was_useful=False,
                                real_outcome="malo")
        uc.execute(dto)
        rule_repo.update.assert_not_called()

    def test_triggers_review_at_threshold(self):
        feedback_repo = MagicMock()
        rule_repo = MagicMock()
        rule = _active_rule()
        feedback_repo.save.side_effect = lambda f: setattr(f, "id", 1) or f
        feedback_repo.get_recent_negatives_for_rule.return_value = _make_negative(NEGATIVE_THRESHOLD)
        rule_repo.get_by_id.return_value = rule

        uc = RecordFeedbackUseCase(feedback_repo, rule_repo)
        dto = FeedbackCreateDTO(decision_id=1, rule_id=1, rating=1, was_useful=False,
                                real_outcome="malo")
        uc.execute(dto)
        rule_repo.update.assert_called_once()
        assert rule.status == RuleStatus.IN_REVIEW

    def test_does_not_retrigger_if_already_in_review(self):
        feedback_repo = MagicMock()
        rule_repo = MagicMock()
        rule = _active_rule()
        rule.status = RuleStatus.IN_REVIEW
        feedback_repo.save.side_effect = lambda f: setattr(f, "id", 1) or f
        feedback_repo.get_recent_negatives_for_rule.return_value = _make_negative(NEGATIVE_THRESHOLD)
        rule_repo.get_by_id.return_value = rule

        uc = RecordFeedbackUseCase(feedback_repo, rule_repo)
        dto = FeedbackCreateDTO(decision_id=1, rule_id=1, rating=1, was_useful=False,
                                real_outcome="malo")
        uc.execute(dto)
        rule_repo.update.assert_not_called()
