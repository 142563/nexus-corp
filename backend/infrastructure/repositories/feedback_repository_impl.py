# infrastructure/repositories/feedback_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.domain.entities.feedback import Feedback
from backend.domain.repositories.feedback_repository import IFeedbackRepository
from backend.infrastructure.database.models import FeedbackModel


class FeedbackRepositoryImpl(IFeedbackRepository):
    def __init__(self, db: Session):
        self._db = db

    def save(self, feedback: Feedback) -> Feedback:
        m = FeedbackModel(
            decision_id=feedback.decision_id, rule_id=feedback.rule_id,
            rating=feedback.rating, was_useful=feedback.was_useful,
            real_outcome=feedback.real_outcome, observations=feedback.observations,
            created_at=feedback.created_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        feedback.id = m.id
        return feedback

    def get_by_rule_id(self, rule_id: int) -> List[Feedback]:
        rows = self._db.query(FeedbackModel).filter(FeedbackModel.rule_id == rule_id).all()
        return [self._to_entity(m) for m in rows]

    def get_recent_negatives_for_rule(self, rule_id: int, last_n: int = 5) -> List[Feedback]:
        recent = (
            self._db.query(FeedbackModel)
            .filter(FeedbackModel.rule_id == rule_id)
            .order_by(FeedbackModel.created_at.desc())
            .limit(last_n)
            .all()
        )
        return [self._to_entity(m) for m in recent if m.rating <= 2 or not m.was_useful]

    def get_average_rating(self, rule_id: int) -> Optional[float]:
        result = (
            self._db.query(func.avg(FeedbackModel.rating))
            .filter(FeedbackModel.rule_id == rule_id)
            .scalar()
        )
        return float(result) if result else None

    def get_all(self) -> List[Feedback]:
        return [self._to_entity(m) for m in self._db.query(FeedbackModel).all()]

    @staticmethod
    def _to_entity(m: FeedbackModel) -> Feedback:
        return Feedback(
            id=m.id, decision_id=m.decision_id, rule_id=m.rule_id,
            rating=m.rating, was_useful=m.was_useful,
            real_outcome=m.real_outcome, observations=m.observations,
            created_at=m.created_at,
        )
