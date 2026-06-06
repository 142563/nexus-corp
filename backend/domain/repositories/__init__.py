# domain/repositories/__init__.py
from .user_repository import IUserRepository
from .expert_repository import IExpertRepository
from .knowledge_area_repository import IKnowledgeAreaRepository
from .business_rule_repository import IBusinessRuleRepository
from .decision_repository import IDecisionRepository
from .feedback_repository import IFeedbackRepository

__all__ = [
    "IUserRepository",
    "IExpertRepository",
    "IKnowledgeAreaRepository",
    "IBusinessRuleRepository",
    "IDecisionRepository",
    "IFeedbackRepository",
]
