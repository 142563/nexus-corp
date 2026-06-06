# domain/entities/expert.py
# Entidad Expert — representa a los expertos del área cuyo conocimiento se captura.
# Capa: Domain.
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExpertStatus(str, Enum):
    ACTIVE = "activo"
    INACTIVE = "inactivo"
    ON_LEAVE = "de_baja"


@dataclass
class Expert:
    id: Optional[int]
    name: str
    position: str
    area: str
    years_experience: int
    email: str
    status: ExpertStatus = ExpertStatus.ACTIVE

    def is_active(self) -> bool:
        return self.status == ExpertStatus.ACTIVE
