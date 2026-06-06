# presentation/routers/knowledge_areas_router.py
# Endpoints de áreas de conocimiento, incluyendo el mapa de conocimiento.
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.knowledge_area_repository_impl import KnowledgeAreaRepositoryImpl
from backend.infrastructure.repositories.expert_repository_impl import ExpertRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles
from backend.domain.entities.user import User, UserRole
from backend.domain.entities.knowledge_area import KnowledgeArea
from backend.application.dtos.knowledge_area_dto import KnowledgeAreaCreateDTO, KnowledgeAreaResponseDTO

router = APIRouter(prefix="/api/v1/knowledge-areas", tags=["Áreas de Conocimiento"])


def _get_repo(db: Session = Depends(get_db)):
    return KnowledgeAreaRepositoryImpl(db)


@router.get("", response_model=List[KnowledgeAreaResponseDTO])
def list_areas(
    repo: KnowledgeAreaRepositoryImpl = Depends(_get_repo),
    _: User = Depends(get_current_user),
):
    return [KnowledgeAreaResponseDTO(id=a.id, name=a.name, description=a.description,
                                     criticality=a.criticality, capture_status=a.capture_status,
                                     expert_id=a.expert_id) for a in repo.get_all()]


@router.post("", response_model=KnowledgeAreaResponseDTO, status_code=status.HTTP_201_CREATED)
def create_area(
    dto: KnowledgeAreaCreateDTO,
    repo: KnowledgeAreaRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)),
):
    area = KnowledgeArea(id=None, name=dto.name, description=dto.description,
                         criticality=dto.criticality, capture_status=dto.capture_status,
                         expert_id=dto.expert_id)
    saved = repo.save(area)
    return KnowledgeAreaResponseDTO(id=saved.id, name=saved.name, description=saved.description,
                                    criticality=saved.criticality, capture_status=saved.capture_status,
                                    expert_id=saved.expert_id)


@router.get("/map")
def knowledge_map(
    area_repo: KnowledgeAreaRepositoryImpl = Depends(_get_repo),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    expert_repo = ExpertRepositoryImpl(db)
    experts = {e.id: e for e in expert_repo.get_all()}
    areas = area_repo.get_all()
    return [
        {
            "area_id": a.id,
            "area_name": a.name,
            "criticality": a.criticality.value,
            "capture_status": a.capture_status.value,
            "expert_id": a.expert_id,
            "expert_name": experts[a.expert_id].name if a.expert_id and a.expert_id in experts else None,
            "expert_position": experts[a.expert_id].position if a.expert_id and a.expert_id in experts else None,
        }
        for a in areas
    ]


@router.get("/{area_id}", response_model=KnowledgeAreaResponseDTO)
def get_area(
    area_id: int,
    repo: KnowledgeAreaRepositoryImpl = Depends(_get_repo),
    _: User = Depends(get_current_user),
):
    area = repo.get_by_id(area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada.")
    return KnowledgeAreaResponseDTO(id=area.id, name=area.name, description=area.description,
                                    criticality=area.criticality, capture_status=area.capture_status,
                                    expert_id=area.expert_id)
