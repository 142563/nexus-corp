# domain/repositories/business_rule_repository.py
# Interfaz abstracta del repositorio de reglas de negocio. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.business_rule import BusinessRule, RuleStatus


class IBusinessRuleRepository(ABC):
    @abstractmethod
    def get_by_id(self, rule_id: int) -> Optional[BusinessRule]: ...

    @abstractmethod
    def get_all(self) -> List[BusinessRule]: ...

    @abstractmethod
    def get_active_rules(self) -> List[BusinessRule]: ...

    @abstractmethod
    def get_by_area(self, area_id: int) -> List[BusinessRule]: ...

    @abstractmethod
    def get_by_status(self, status: RuleStatus) -> List[BusinessRule]: ...

    @abstractmethod
    def save(self, rule: BusinessRule) -> BusinessRule: ...

    @abstractmethod
    def update(self, rule: BusinessRule) -> BusinessRule: ...

    @abstractmethod
    def delete(self, rule_id: int) -> None: ...
