# presentation/routers/users_router.py
# Gestión de usuarios del sistema. Solo system_admin puede crear y cambiar roles.
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from backend.infrastructure.security.auth import get_current_user, require_roles, hash_password
from backend.domain.entities.user import User, UserRole, UserStatus
from backend.application.dtos.user_dto import UserCreateDTO, UserResponseDTO, UserUpdateRoleDTO

router = APIRouter(prefix="/api/v1/users", tags=["Usuarios"])


def _get_repo(db: Session = Depends(get_db)):
    return UserRepositoryImpl(db)


@router.get("", response_model=List[UserResponseDTO])
def list_users(
    repo: UserRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.KNOWLEDGE_ADMIN)),
):
    users = repo.get_all()
    return [UserResponseDTO(id=u.id, name=u.name, email=u.email, role=u.role,
                            status=u.status, created_at=u.created_at) for u in users]


@router.post("", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    dto: UserCreateDTO,
    repo: UserRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    existing = repo.get_by_email(dto.email)
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    user = User(id=None, name=dto.name, email=dto.email,
                hashed_password=hash_password(dto.password), role=dto.role)
    saved = repo.save(user)
    return UserResponseDTO(id=saved.id, name=saved.name, email=saved.email,
                           role=saved.role, status=saved.status, created_at=saved.created_at)


@router.patch("/{user_id}/role", response_model=UserResponseDTO)
def update_user_role(
    user_id: int,
    dto: UserUpdateRoleDTO,
    repo: UserRepositoryImpl = Depends(_get_repo),
    _: User = Depends(require_roles(UserRole.SYSTEM_ADMIN)),
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.role = dto.role
    updated = repo.update(user)
    return UserResponseDTO(id=updated.id, name=updated.name, email=updated.email,
                           role=updated.role, status=updated.status, created_at=updated.created_at)
