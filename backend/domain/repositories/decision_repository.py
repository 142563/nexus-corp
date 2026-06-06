# domain/repositories/decision_repository.py
# Interfaz abstracta del repositorio de decisiones. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.decision import DecisionRequest, DecisionRecommendation, DecisionRecord


class IDecisionRepository(ABC):
    @abstractmethod
    def save_request(self, request: DecisionRequest) -> DecisionRequest: ...

    @abstractmethod
    def save_recommendation(self, rec: DecisionRecommendation) -> DecisionRecommendation: ...

    @abstractmethod
    def save_record(self, record: DecisionRecord) -> DecisionRecord: ...

    @abstractmethod
    def get_request_by_id(self, request_id: int) -> Optional[DecisionRequest]: ...

    @abstractmethod
    def get_recommendation_by_id(self, rec_id: int) -> Optional[DecisionRecommendation]: ...

    @abstractmethod
    def get_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[dict]: ...
