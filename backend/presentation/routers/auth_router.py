# presentation/routers/auth_router.py
# Endpoints de autenticación: login y refresh de token.
# Capa: Presentation. Solo orquesta, no contiene lógica de negocio.
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.infrastructure.database.connection import get_db
from backend.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from backend.infrastructure.security.auth import (
    verify_password, create_access_token, get_current_user
)
from backend.domain.entities.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: str


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    repo = UserRepositoryImpl(db)
    user = repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )
    if not user.is_active():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo.")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.id,
        name=user.name,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    token = create_access_token({"sub": str(current_user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=current_user.role.value,
        user_id=current_user.id,
        name=current_user.name,
    )
