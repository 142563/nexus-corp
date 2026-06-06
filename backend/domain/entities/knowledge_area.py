# domain/entities/knowledge_area.py
# Entidad KnowledgeArea — área de conocimiento organizacional de DistribLog S.A.
# Capa: Domain.
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CaptureStatus(str, Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completado"
    VALIDATED = "validado"


class Criticality(str, Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"


@dataclass
class KnowledgeArea:
    id: Optional[int]
    name: str
    description: str
    criticality: Criticality
    capture_status: CaptureStatus
    expert_id: Optional[int]

    def is_ready_for_rules(self) -> bool:
        return self.capture_status in (CaptureStatus.COMPLETED, CaptureStatus.VALIDATED)
