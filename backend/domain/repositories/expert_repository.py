# domain/repositories/expert_repository.py
# Interfaz abstracta del repositorio de expertos. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.expert import Expert


class IExpertRepository(ABC):
    @abstractmethod
    def get_by_id(self, expert_id: int) -> Optional[Expert]: ...

    @abstractmethod
    def get_all(self) -> List[Expert]: ...

    @abstractmethod
    def save(self, expert: Expert) -> Expert: ...

    @abstractmethod
    def update(self, expert: Expert) -> Expert: ...

    @abstractmethod
    def delete(self, expert_id: int) -> None: ...
