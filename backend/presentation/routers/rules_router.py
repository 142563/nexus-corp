# presentation/routers/rules_router.py
# CRUD de reglas de negocio con control de acceso por rol.
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.business_rule_repository_impl import BusinessRuleRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles
from backend.domain.entities.user import User, UserRole
from backend.application.use_cases.manage_business_rule import ManageBusinessRuleUseCase
from backend.application.dtos.business_rule_dto import (
    BusinessRuleCreateDTO, BusinessRuleResponseDTO,
    BusinessRuleUpdateDTO, RuleStatusUpdateDTO,
)

router = APIRouter(prefix="/api/v1/rules", tags=["Reglas de Negocio"])


def _get_use_case(db: Session = Depends(get_db)) -> ManageBusinessRuleUseCase:
    return ManageBusinessRuleUseCase(BusinessRuleRepositoryImpl(db))


@router.get("", response_model=List[BusinessRuleResponseDTO])
def list_rules(
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(get_current_user),
):
    return uc.get_all()


@router.post("", response_model=BusinessRuleResponseDTO, status_code=status.HTTP_201_CREATED)
def create_rule(
    dto: BusinessRuleCreateDTO,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    return uc.create(dto)


@router.get("/{rule_id}", response_model=BusinessRuleResponseDTO)
def get_rule(
    rule_id: int,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(get_current_user),
):
    rule = uc.get_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    return rule


@router.put("/{rule_id}", response_model=BusinessRuleResponseDTO)
def update_rule(
    rule_id: int,
    dto: BusinessRuleUpdateDTO,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    try:
        return uc.update(rule_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{rule_id}/status", response_model=BusinessRuleResponseDTO)
def change_rule_status(
    rule_id: int,
    dto: RuleStatusUpdateDTO,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    try:
        return uc.change_status(rule_id, dto.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{rule_id}/validate", response_model=BusinessRuleResponseDTO)
def validate_rule(
    rule_id: int,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    current_user: User = Depends(require_roles(
        UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN, UserRole.AREA_EXPERT
    )),
):
    from backend.domain.entities.business_rule import RuleStatus
    try:
        return uc.change_status(rule_id, RuleStatus.ACTIVE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    uc: ManageBusinessRuleUseCase = Depends(_get_use_case),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    uc.delete(rule_id)
