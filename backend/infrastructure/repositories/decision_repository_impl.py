# infrastructure/repositories/decision_repository_impl.py
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from backend.domain.entities.decision import DecisionRequest, DecisionRecommendation, DecisionRecord
from backend.domain.repositories.decision_repository import IDecisionRepository
from backend.infrastructure.database.models import (
    DecisionRequestModel, DecisionRecommendationModel, DecisionRecordModel
)


class DecisionRepositoryImpl(IDecisionRepository):
    def __init__(self, db: Session):
        self._db = db

    def save_request(self, request: DecisionRequest) -> DecisionRequest:
        m = DecisionRequestModel(
            user_id=request.user_id, input_data=request.input_data,
            request_type=request.request_type, requested_at=request.requested_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        request.id = m.id
        return request

    def save_recommendation(self, rec: DecisionRecommendation) -> DecisionRecommendation:
        m = DecisionRecommendationModel(
            request_id=rec.request_id, activated_rules=rec.activated_rules,
            suggested_action=rec.suggested_action, confidence=rec.confidence,
            explanation=rec.explanation, estimated_risk=rec.estimated_risk,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        rec.id = m.id
        return rec

    def save_record(self, record: DecisionRecord) -> DecisionRecord:
        m = DecisionRecordModel(
            recommendation_id=record.recommendation_id, user_id=record.user_id,
            outcome=record.outcome, justification=record.justification,
            decided_at=record.decided_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        record.id = m.id
        return record

    def get_request_by_id(self, request_id: int) -> Optional[DecisionRequest]:
        m = self._db.query(DecisionRequestModel).filter(DecisionRequestModel.id == request_id).first()
        if not m:
            return None
        return DecisionRequest(id=m.id, user_id=m.user_id, input_data=m.input_data,
                               request_type=m.request_type, requested_at=m.requested_at)

    def get_recommendation_by_id(self, rec_id: int) -> Optional[DecisionRecommendation]:
        m = self._db.query(DecisionRecommendationModel).filter(DecisionRecommendationModel.id == rec_id).first()
        if not m:
            return None
        return DecisionRecommendation(
            id=m.id, request_id=m.request_id, activated_rules=m.activated_rules,
            suggested_action=m.suggested_action, confidence=m.confidence,
            explanation=m.explanation, estimated_risk=m.estimated_risk,
        )

    def get_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        query = (
            self._db.query(
                DecisionRequestModel, DecisionRecommendationModel, DecisionRecordModel
            )
            .join(DecisionRecommendationModel, DecisionRecommendationModel.request_id == DecisionRequestModel.id, isouter=True)
            .join(DecisionRecordModel, DecisionRecordModel.recommendation_id == DecisionRecommendationModel.id, isouter=True)
        )
        if user_id:
            query = query.filter(DecisionRequestModel.user_id == user_id)
        rows = query.order_by(DecisionRequestModel.requested_at.desc()).limit(limit).all()
        result = []
        for req, rec, record in rows:
            result.append({
                "request_id": req.id,
                "user_id": req.user_id,
                "request_type": req.request_type,
                "requested_at": req.requested_at,
                "recommendation_id": rec.id if rec else None,
                "suggested_action": rec.suggested_action if rec else None,
                "confidence": rec.confidence if rec else None,
                "estimated_risk": rec.estimated_risk if rec else None,
                "outcome": record.outcome if record else None,
                "decided_at": record.decided_at if record else None,
            })
        return result
