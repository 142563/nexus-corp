# presentation/routers/whatif_router.py
# Análisis What-If: escenarios hipotéticos sin persistencia en historial real.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.business_rule_repository_impl import BusinessRuleRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles
from backend.domain.entities.user import User, UserRole
from backend.domain.rule_engine import RuleEngine
from backend.application.use_cases.whatif_analysis import WhatIfAnalysisUseCase
from backend.application.dtos.decision_dto import WhatIfScenarioDTO, WhatIfCompareDTO

router = APIRouter(prefix="/api/v1/whatif", tags=["Análisis What-If"])


def _get_uc(db: Session = Depends(get_db)) -> WhatIfAnalysisUseCase:
    return WhatIfAnalysisUseCase(BusinessRuleRepositoryImpl(db), RuleEngine())


@router.post("/scenarios")
def evaluate_scenario(
    dto: WhatIfScenarioDTO,
    uc: WhatIfAnalysisUseCase = Depends(_get_uc),
    _: User = Depends(require_roles(
        UserRole.ANALYST, UserRole.DECISION_MAKER,
        UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN
    )),
):
    return uc.evaluate_scenario(dto).to_dict()


@router.post("/compare")
def compare_scenarios(
    dto: WhatIfCompareDTO,
    uc: WhatIfAnalysisUseCase = Depends(_get_uc),
    _: User = Depends(require_roles(
        UserRole.ANALYST, UserRole.DECISION_MAKER,
        UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN
    )),
):
    return uc.compare_scenarios(dto.scenarios)
