# application/use_cases/record_feedback.py
# Registra retroalimentación y aplica RN-005: marca la regla en revisión si acumula
# 3 o más calificaciones negativas en las últimas 5 aplicaciones.
# Capa: Application.
from backend.domain.entities.feedback import Feedback
from backend.domain.entities.business_rule import RuleStatus
from backend.domain.repositories import IFeedbackRepository, IBusinessRuleRepository
from backend.application.dtos.feedback_dto import FeedbackCreateDTO, FeedbackResponseDTO


NEGATIVE_THRESHOLD = 3   # RN-005
REVIEW_WINDOW = 5         # últimas N aplicaciones


class RecordFeedbackUseCase:
    def __init__(
        self,
        feedback_repo: IFeedbackRepository,
        rule_repo: IBusinessRuleRepository,
    ):
        self._feedback_repo = feedback_repo
        self._rule_repo = rule_repo

    def execute(self, dto: FeedbackCreateDTO) -> FeedbackResponseDTO:
        feedback = Feedback(
            id=None,
            decision_id=dto.decision_id,
            rule_id=dto.rule_id,
            rating=dto.rating,
            was_useful=dto.was_useful,
            real_outcome=dto.real_outcome,
            observations=dto.observations,
        )
        saved = self._feedback_repo.save(feedback)

        # RN-005: si hay >= NEGATIVE_THRESHOLD negativos en las últimas REVIEW_WINDOW evaluaciones
        recent = self._feedback_repo.get_recent_negatives_for_rule(dto.rule_id, REVIEW_WINDOW)
        if len(recent) >= NEGATIVE_THRESHOLD:
            rule = self._rule_repo.get_by_id(dto.rule_id)
            if rule and rule.status == RuleStatus.ACTIVE:
                rule.mark_for_review()
                self._rule_repo.update(rule)

        return FeedbackResponseDTO(
            id=saved.id,
            decision_id=saved.decision_id,
            rule_id=saved.rule_id,
            rating=saved.rating,
            was_useful=saved.was_useful,
            real_outcome=saved.real_outcome,
            observations=saved.observations,
            created_at=saved.created_at,
        )
