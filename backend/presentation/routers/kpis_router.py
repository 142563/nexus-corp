# presentation/routers/kpis_router.py
# Endpoints del dashboard ejecutivo de KPIs y tendencias.
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.business_rule_repository_impl import BusinessRuleRepositoryImpl
from backend.infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from backend.infrastructure.repositories.feedback_repository_impl import FeedbackRepositoryImpl
from backend.infrastructure.security.auth import require_roles
from backend.domain.entities.user import User, UserRole
from backend.application.use_cases.get_kpi_dashboard import GetKPIDashboardUseCase
from backend.application.dtos.kpi_dto import KPIDashboardDTO, KPITrendsDTO

router = APIRouter(prefix="/api/v1/kpis", tags=["KPIs"])


def _get_uc(db: Session = Depends(get_db)) -> GetKPIDashboardUseCase:
    return GetKPIDashboardUseCase(
        rule_repo=BusinessRuleRepositoryImpl(db),
        decision_repo=DecisionRepositoryImpl(db),
        feedback_repo=FeedbackRepositoryImpl(db),
    )


@router.get("/dashboard", response_model=KPIDashboardDTO)
def get_dashboard(
    uc: GetKPIDashboardUseCase = Depends(_get_uc),
    _: User = Depends(require_roles(
        UserRole.ANALYST, UserRole.KNOWLEDGE_ADMIN,
        UserRole.SYSTEM_ADMIN, UserRole.DECISION_MAKER
    )),
):
    return uc.get_dashboard()


@router.get("/trends", response_model=KPITrendsDTO)
def get_trends(
    days: int = Query(default=30, ge=7, le=90),
    uc: GetKPIDashboardUseCase = Depends(_get_uc),
    _: User = Depends(require_roles(
        UserRole.ANALYST, UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN
    )),
):
    return uc.get_trends(days=days)
