# application/dtos/user_dto.py
# DTOs de usuario — contratos de entrada/salida para la capa de presentación.
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from backend.domain.entities.user import UserRole, UserStatus


class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.ANALYST


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRoleDTO(BaseModel):
    role: UserRole
