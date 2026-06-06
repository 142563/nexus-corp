# application/dtos/knowledge_area_dto.py
from pydantic import BaseModel
from typing import Optional
from backend.domain.entities.knowledge_area import CaptureStatus, Criticality


class KnowledgeAreaCreateDTO(BaseModel):
    name: str
    description: str
    criticality: Criticality
    capture_status: CaptureStatus = CaptureStatus.PENDING
    expert_id: Optional[int] = None


class KnowledgeAreaResponseDTO(BaseModel):
    id: int
    name: str
    description: str
    criticality: Criticality
    capture_status: CaptureStatus
    expert_id: Optional[int]

    model_config = {"from_attributes": True}
