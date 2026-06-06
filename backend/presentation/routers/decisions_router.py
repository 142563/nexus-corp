# presentation/routers/decisions_router.py
# Endpoints del motor de decisiones y registro de decisiones tomadas.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.business_rule_repository_impl import BusinessRuleRepositoryImpl
from backend.infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles
from backend.domain.entities.user import User, UserRole
from backend.domain.rule_engine import RuleEngine
from backend.application.use_cases.evaluate_situation import EvaluateSituationUseCase
from backend.application.dtos.decision_dto import (
    EvaluateSituationDTO, DecisionResponseDTO, RecordDecisionDTO
)
from backend.domain.entities.decision import DecisionRecord

router = APIRouter(prefix="/api/v1/decisions", tags=["Decisiones"])


def _get_evaluate_uc(db: Session = Depends(get_db)) -> EvaluateSituationUseCase:
    return EvaluateSituationUseCase(
        rule_repo=BusinessRuleRepositoryImpl(db),
        decision_repo=DecisionRepositoryImpl(db),
        rule_engine=RuleEngine(),
    )


@router.post("/evaluate", response_model=DecisionResponseDTO)
def evaluate_situation(
    dto: EvaluateSituationDTO,
    uc: EvaluateSituationUseCase = Depends(_get_evaluate_uc),
    current_user: User = Depends(require_roles(
        UserRole.DECISION_MAKER, UserRole.SYSTEM_ADMIN, UserRole.KNOWLEDGE_ADMIN
    )),
):
    return uc.execute(dto, current_user.id)


@router.get("/history")
def decision_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DecisionRepositoryImpl(db)
    uid = current_user.id if current_user.role not in (UserRole.SYSTEM_ADMIN, UserRole.ANALYST) else None
    return repo.get_history(user_id=uid, limit=100)


@router.post("/{recommendation_id}/record")
def record_decision(
    recommendation_id: int,
    dto: RecordDecisionDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.DECISION_MAKER, UserRole.SYSTEM_ADMIN
    )),
):
    repo = DecisionRepositoryImpl(db)
    rec = repo.get_recommendation_by_id(recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recomendación no encontrada.")
    record = DecisionRecord(
        id=None, recommendation_id=recommendation_id,
        user_id=current_user.id, outcome=dto.outcome, justification=dto.justification,
    )
    saved = repo.save_record(record)
    return {"record_id": saved.id, "outcome": saved.outcome, "decided_at": saved.decided_at}
