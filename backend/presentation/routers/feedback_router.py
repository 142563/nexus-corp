# presentation/routers/feedback_router.py
# Endpoints de retroalimentación sobre decisiones.
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.feedback_repository_impl import FeedbackRepositoryImpl
from backend.infrastructure.repositories.business_rule_repository_impl import BusinessRuleRepositoryImpl
from backend.infrastructure.security.auth import get_current_user
from backend.domain.entities.user import User
from backend.application.use_cases.record_feedback import RecordFeedbackUseCase
from backend.application.dtos.feedback_dto import FeedbackCreateDTO, FeedbackResponseDTO

router = APIRouter(prefix="/api/v1/feedback", tags=["Retroalimentación"])


def _get_uc(db: Session = Depends(get_db)) -> RecordFeedbackUseCase:
    return RecordFeedbackUseCase(FeedbackRepositoryImpl(db), BusinessRuleRepositoryImpl(db))


@router.post("", response_model=FeedbackResponseDTO)
def create_feedback(
    dto: FeedbackCreateDTO,
    uc: RecordFeedbackUseCase = Depends(_get_uc),
    _: User = Depends(get_current_user),
):
    return uc.execute(dto)


@router.get("/rule/{rule_id}", response_model=List[FeedbackResponseDTO])
def feedback_by_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = FeedbackRepositoryImpl(db)
    return [
        FeedbackResponseDTO(id=f.id, decision_id=f.decision_id, rule_id=f.rule_id,
                            rating=f.rating, was_useful=f.was_useful, real_outcome=f.real_outcome,
                            observations=f.observations, created_at=f.created_at)
        for f in repo.get_by_rule_id(rule_id)
    ]
