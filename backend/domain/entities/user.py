# domain/entities/user.py
# Entidad User — representa a los usuarios del sistema Nexus-Corp.
# Capa: Domain. No depende de ninguna capa externa.
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    KNOWLEDGE_ADMIN = "knowledge_admin"
    DECISION_MAKER = "decision_maker"
    ANALYST = "analyst"
    AREA_EXPERT = "area_expert"
    SYSTEM_ADMIN = "system_admin"


class UserStatus(str, Enum):
    ACTIVE = "activo"
    INACTIVE = "inactivo"
    SUSPENDED = "suspendido"


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    hashed_password: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def can_manage_rules(self) -> bool:
        return self.role in (UserRole.KNOWLEDGE_ADMIN, UserRole.SYSTEM_ADMIN)

    def can_make_decisions(self) -> bool:
        return self.role in (UserRole.DECISION_MAKER, UserRole.SYSTEM_ADMIN)

    def can_view_analytics(self) -> bool:
        return self.role in (UserRole.ANALYST, UserRole.SYSTEM_ADMIN, UserRole.KNOWLEDGE_ADMIN)
