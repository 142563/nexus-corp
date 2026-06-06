# application/dtos/expert_dto.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.domain.entities.expert import ExpertStatus


class ExpertCreateDTO(BaseModel):
    name: str
    position: str
    area: str
    years_experience: int
    email: EmailStr
    status: ExpertStatus = ExpertStatus.ACTIVE


class ExpertUpdateDTO(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    area: Optional[str] = None
    years_experience: Optional[int] = None
    email: Optional[EmailStr] = None
    status: Optional[ExpertStatus] = None


class ExpertResponseDTO(BaseModel):
    id: int
    name: str
    position: str
    area: str
    years_experience: int
    email: str
    status: ExpertStatus

    model_config = {"from_attributes": True}
