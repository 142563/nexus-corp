# domain/repositories/user_repository.py
# Interfaz abstracta del repositorio de usuarios. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def get_all(self) -> List[User]: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def update(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...
