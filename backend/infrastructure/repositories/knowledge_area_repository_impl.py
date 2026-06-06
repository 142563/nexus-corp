# infrastructure/repositories/knowledge_area_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.domain.entities.knowledge_area import KnowledgeArea, CaptureStatus, Criticality
from backend.domain.repositories.knowledge_area_repository import IKnowledgeAreaRepository
from backend.infrastructure.database.models import KnowledgeAreaModel


class KnowledgeAreaRepositoryImpl(IKnowledgeAreaRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, area_id: int) -> Optional[KnowledgeArea]:
        m = self._db.query(KnowledgeAreaModel).filter(KnowledgeAreaModel.id == area_id).first()
        return self._to_entity(m) if m else None

    def get_all(self) -> List[KnowledgeArea]:
        return [self._to_entity(m) for m in self._db.query(KnowledgeAreaModel).all()]

    def get_by_expert_id(self, expert_id: int) -> List[KnowledgeArea]:
        rows = self._db.query(KnowledgeAreaModel).filter(KnowledgeAreaModel.expert_id == expert_id).all()
        return [self._to_entity(m) for m in rows]

    def save(self, area: KnowledgeArea) -> KnowledgeArea:
        m = KnowledgeAreaModel(
            name=area.name, description=area.description,
            criticality=area.criticality.value, capture_status=area.capture_status.value,
            expert_id=area.expert_id,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def update(self, area: KnowledgeArea) -> KnowledgeArea:
        m = self._db.query(KnowledgeAreaModel).filter(KnowledgeAreaModel.id == area.id).first()
        if not m:
            raise ValueError(f"Área {area.id} no encontrada.")
        m.name = area.name
        m.description = area.description
        m.criticality = area.criticality.value
        m.capture_status = area.capture_status.value
        m.expert_id = area.expert_id
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def delete(self, area_id: int) -> None:
        m = self._db.query(KnowledgeAreaModel).filter(KnowledgeAreaModel.id == area_id).first()
        if m:
            self._db.delete(m)
            self._db.commit()

    @staticmethod
    def _to_entity(m: KnowledgeAreaModel) -> KnowledgeArea:
        return KnowledgeArea(
            id=m.id, name=m.name, description=m.description,
            criticality=Criticality(m.criticality), capture_status=CaptureStatus(m.capture_status),
            expert_id=m.expert_id,
        )
