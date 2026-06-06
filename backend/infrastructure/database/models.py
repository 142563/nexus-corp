# infrastructure/database/models.py
# Modelos SQLAlchemy para DistribLog S.A. — mapeo ORM de las entidades del dominio.
# Capa: Infrastructure. Traduce entre la BD relacional y las entidades del dominio.
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, JSON, String, Text
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="activo")
    created_at = Column(DateTime, default=datetime.utcnow)


class ExpertModel(Base):
    __tablename__ = "experts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    area = Column(String(200), nullable=False)
    years_experience = Column(Integer, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="activo")

    knowledge_areas = relationship("KnowledgeAreaModel", back_populates="expert")


class KnowledgeAreaModel(Base):
    __tablename__ = "knowledge_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    criticality = Column(String(50), nullable=False)
    capture_status = Column(String(50), nullable=False, default="pendiente")
    expert_id = Column(Integer, ForeignKey("experts.id"), nullable=True)

    expert = relationship("ExpertModel", back_populates="knowledge_areas")
    rules = relationship("BusinessRuleModel", back_populates="area")


class BusinessRuleModel(Base):
    __tablename__ = "business_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    conditions = Column(JSON, nullable=False)
    suggested_action = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=5)
    area_id = Column(Integer, ForeignKey("knowledge_areas.id"), nullable=False)
    expert_id = Column(Integer, ForeignKey("experts.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pendiente")
    confidence_level = Column(Float, nullable=False, default=0.80)
    user_explanation = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed_at = Column(DateTime, nullable=True)

    area = relationship("KnowledgeAreaModel", back_populates="rules")

    feedback_entries = relationship("FeedbackModel", back_populates="rule")


class DecisionRequestModel(Base):
    __tablename__ = "decision_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_data = Column(JSON, nullable=False)
    request_type = Column(String(100), nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("DecisionRecommendationModel", back_populates="request", uselist=False)


class DecisionRecommendationModel(Base):
    __tablename__ = "decision_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("decision_requests.id"), nullable=False)
    activated_rules = Column(JSON, nullable=False)
    suggested_action = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    estimated_risk = Column(String(50), nullable=False)

    request = relationship("DecisionRequestModel", back_populates="recommendation")
    record = relationship("DecisionRecordModel", back_populates="recommendation", uselist=False)


class DecisionRecordModel(Base):
    __tablename__ = "decision_records"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("decision_recommendations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outcome = Column(String(100), nullable=False)
    justification = Column(Text, nullable=False)
    decided_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("DecisionRecommendationModel", back_populates="record")


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decision_records.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("business_rules.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    was_useful = Column(Boolean, nullable=False)
    real_outcome = Column(String(200), nullable=False)
    observations = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    rule = relationship("BusinessRuleModel", back_populates="feedback_entries")


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
