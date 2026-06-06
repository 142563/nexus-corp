# presentation/routers/experts_router.py
# CRUD de expertos. Requiere autenticación. Modificaciones requieren knowledge_admin/system_admin.
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.expert_repository_impl import ExpertRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles
from backend.domain.entities.user import User, UserRole
from backend.domain.entities.expert import Expert, ExpertStatus
from backend.application.dtos.expert_dto import ExpertCreateDTO, ExpertResponseDTO, ExpertUpdateDTO

router = APIRouter(prefix="/api/v1/experts", tags=["Expertos"])


def _get_repo(db: Session = Depends(get_db)) -> ExpertRepositoryImpl:
    return ExpertRepositoryImpl(db)


@router.get("", response_model=List[ExpertResponseDTO])
def list_experts(
    repo: ExpertRepositoryImpl = Depends(_get_repo),
    _: User = Depends(get_current_user),
):
    return [ExpertResponseDTO.model_validate(e.__dict__ | {"id": e.id}) for e in repo.get_all()]


@router.post("", response_model=ExpertResponseDTO, status_code=status.HTTP_201_CREATED)
def create_expert(
    dto: ExpertCreateDTO,
    repo: ExpertRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    expert = Expert(id=None, name=dto.name, position=dto.position, area=dto.area,
                    years_experience=dto.years_experience, email=dto.email, status=dto.status)
    saved = repo.save(expert)
    return ExpertResponseDTO(id=saved.id, name=saved.name, position=saved.position,
                             area=saved.area, years_experience=saved.years_experience,
                             email=saved.email, status=saved.status)


@router.get("/{expert_id}", response_model=ExpertResponseDTO)
def get_expert(
    expert_id: int,
    repo: ExpertRepositoryImpl = Depends(_get_repo),
    _: User = Depends(get_current_user),
):
    expert = repo.get_by_id(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Experto no encontrado.")
    return ExpertResponseDTO(id=expert.id, name=expert.name, position=expert.position,
                             area=expert.area, years_experience=expert.years_experience,
                             email=expert.email, status=expert.status)


@router.put("/{expert_id}", response_model=ExpertResponseDTO)
def update_expert(
    expert_id: int,
    dto: ExpertUpdateDTO,
    repo: ExpertRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    expert = repo.get_by_id(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Experto no encontrado.")
    if dto.name is not None:
        expert.name = dto.name
    if dto.position is not None:
        expert.position = dto.position
    if dto.area is not None:
        expert.area = dto.area
    if dto.years_experience is not None:
        expert.years_experience = dto.years_experience
    if dto.email is not None:
        expert.email = dto.email
    if dto.status is not None:
        expert.status = dto.status
    updated = repo.update(expert)
    return ExpertResponseDTO(id=updated.id, name=updated.name, position=updated.position,
                             area=updated.area, years_experience=updated.years_experience,
                             email=updated.email, status=updated.status)


@router.delete("/{expert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expert(
    expert_id: int,
    repo: ExpertRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    repo.delete(expert_id)
