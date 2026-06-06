# infrastructure/repositories/user_repository_impl.py
# Implementación concreta del repositorio de usuarios con SQLAlchemy.
# Capa: Infrastructure.
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.domain.entities.user import User, UserRole, UserStatus
from backend.domain.repositories.user_repository import IUserRepository
from backend.infrastructure.database.models import UserModel


class UserRepositoryImpl(IUserRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self._db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def get_all(self) -> List[User]:
        return [self._to_entity(m) for m in self._db.query(UserModel).all()]

    def save(self, user: User) -> User:
        model = UserModel(
            name=user.name,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            status=user.status.value,
            created_at=user.created_at,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, user: User) -> User:
        model = self._db.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError(f"Usuario {user.id} no encontrado.")
        model.name = user.name
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.role = user.role.value
        model.status = user.status.value
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: int) -> None:
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self._db.delete(model)
            self._db.commit()

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            created_at=model.created_at,
        )
