# domain/repositories/feedback_repository.py
# Interfaz abstracta del repositorio de retroalimentación. Capa: Domain.
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.feedback import Feedback


class IFeedbackRepository(ABC):
    @abstractmethod
    def save(self, feedback: Feedback) -> Feedback: ...

    @abstractmethod
    def get_by_rule_id(self, rule_id: int) -> List[Feedback]: ...

    @abstractmethod
    def get_recent_negatives_for_rule(self, rule_id: int, last_n: int = 5) -> List[Feedback]: ...

    @abstractmethod
    def get_average_rating(self, rule_id: int) -> Optional[float]: ...

    @abstractmethod
    def get_all(self) -> List[Feedback]: ...
