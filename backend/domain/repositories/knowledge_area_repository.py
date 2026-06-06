# domain/repositories/knowledge_area_repository.py
# Interfaz abstracta del repositorio de áreas de conocimiento. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.knowledge_area import KnowledgeArea


class IKnowledgeAreaRepository(ABC):
    @abstractmethod
    def get_by_id(self, area_id: int) -> Optional[KnowledgeArea]: ...

    @abstractmethod
    def get_all(self) -> List[KnowledgeArea]: ...

    @abstractmethod
    def get_by_expert_id(self, expert_id: int) -> List[KnowledgeArea]: ...

    @abstractmethod
    def save(self, area: KnowledgeArea) -> KnowledgeArea: ...

    @abstractmethod
    def update(self, area: KnowledgeArea) -> KnowledgeArea: ...

    @abstractmethod
    def delete(self, area_id: int) -> None: ...
