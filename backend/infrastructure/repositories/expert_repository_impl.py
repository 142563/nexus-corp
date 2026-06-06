# infrastructure/repositories/expert_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.domain.entities.expert import Expert, ExpertStatus
from backend.domain.repositories.expert_repository import IExpertRepository
from backend.infrastructure.database.models import ExpertModel


class ExpertRepositoryImpl(IExpertRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, expert_id: int) -> Optional[Expert]:
        m = self._db.query(ExpertModel).filter(ExpertModel.id == expert_id).first()
        return self._to_entity(m) if m else None

    def get_all(self) -> List[Expert]:
        return [self._to_entity(m) for m in self._db.query(ExpertModel).all()]

    def save(self, expert: Expert) -> Expert:
        m = ExpertModel(
            name=expert.name, position=expert.position, area=expert.area,
            years_experience=expert.years_experience, email=expert.email,
            status=expert.status.value,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def update(self, expert: Expert) -> Expert:
        m = self._db.query(ExpertModel).filter(ExpertModel.id == expert.id).first()
        if not m:
            raise ValueError(f"Experto {expert.id} no encontrado.")
        m.name = expert.name
        m.position = expert.position
        m.area = expert.area
        m.years_experience = expert.years_experience
        m.email = expert.email
        m.status = expert.status.value
        self._db.commit()
        self._db.refresh(m)
        return self._to_entity(m)

    def delete(self, expert_id: int) -> None:
        m = self._db.query(ExpertModel).filter(ExpertModel.id == expert_id).first()
        if m:
            self._db.delete(m)
            self._db.commit()

    @staticmethod
    def _to_entity(m: ExpertModel) -> Expert:
        return Expert(
            id=m.id, name=m.name, position=m.position, area=m.area,
            years_experience=m.years_experience, email=m.email,
            status=ExpertStatus(m.status),
        )
