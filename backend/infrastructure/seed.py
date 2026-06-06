# infrastructure/seed.py
# Carga los datos iniciales de DistribLog S.A.: expertos, áreas, reglas y usuarios.
# Solo inserta si la base de datos está vacía para evitar duplicados.
from datetime import datetime
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.database.models import (
    UserModel, ExpertModel, KnowledgeAreaModel, BusinessRuleModel
)
from backend.infrastructure.security.auth import hash_password


def run_seed(engine: Engine) -> None:
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        if db.query(UserModel).count() > 0:
            return  # ya fue inicializado

        # ── Usuarios ──────────────────────────────────────────────────────
        admin = UserModel(
            name="Administrador Sistema",
            email="admin@nexuscorp.com",
            hashed_password=hash_password("Admin2026!"),
            role="system_admin",
            status="activo",
        )
        decisor = UserModel(
            name="Decisor Prueba",
            email="decisor@nexuscorp.com",
            hashed_password=hash_password("Decisor2026!"),
            role="decision_maker",
            status="activo",
        )
        db.add_all([admin, decisor])
        db.flush()

        # ── Expertos ──────────────────────────────────────────────────────
        expertos = [
            ExpertModel(name="Roberto Morales", position="Jefe de Rutas",
                        area="Gestión de Rutas", years_experience=12, email="rmorales@distriblog.gt", status="activo"),
            ExpertModel(name="Carmen Estrada", position="Supervisora de Inventario",
                        area="Inventario", years_experience=9, email="cestrada@distriblog.gt", status="activo"),
            ExpertModel(name="Miguel Herrera", position="Coordinador de Pedidos",
                        area="Pedidos", years_experience=7, email="mherrera@distriblog.gt", status="activo"),
            ExpertModel(name="Lucía Pérez", position="Gerente de Recursos",
                        area="Recursos", years_experience=15, email="lperez@distriblog.gt", status="activo"),
            ExpertModel(name="Jorge Castillo", position="Analista de Riesgos",
                        area="Riesgos", years_experience=11, email="jcastillo@distriblog.gt", status="activo"),
        ]
        db.add_all(expertos)
        db.flush()

        # ── Áreas de conocimiento ─────────────────────────────────────────
        areas = [
            KnowledgeAreaModel(name="Gestión de Rutas", description="Planificación y optimización de rutas de entrega.",
                               criticality="alta", capture_status="validado", expert_id=expertos[0].id),
            KnowledgeAreaModel(name="Inventario", description="Control y disponibilidad de productos en bodega.",
                               criticality="critica", capture_status="validado", expert_id=expertos[1].id),
            KnowledgeAreaModel(name="Pedidos", description="Gestión del ciclo completo de pedidos mayoristas.",
                               criticality="alta", capture_status="completado", expert_id=expertos[2].id),
            KnowledgeAreaModel(name="Recursos", description="Asignación de vehículos, personal y activos logísticos.",
                               criticality="media", capture_status="validado", expert_id=expertos[3].id),
            KnowledgeAreaModel(name="Riesgos", description="Identificación y mitigación de riesgos operativos.",
                               criticality="critica", capture_status="validado", expert_id=expertos[4].id),
        ]
        db.add_all(areas)
        db.flush()

        # ── Reglas de negocio (RN-001 a RN-005) ──────────────────────────
        reglas = [
            BusinessRuleModel(
                name="RN-001: Reasignación por retraso crítico",
                description="Si el pedido es de alta prioridad y lleva más de 120 minutos de retraso, reasignar recursos de forma inmediata.",
                conditions=[
                    {"field": "order_priority", "operator": "eq", "value": "alta"},
                    {"field": "delay_minutes", "operator": "gt", "value": 120},
                ],
                suggested_action="Reasignar recursos inmediatamente al pedido y notificar al supervisor.",
                priority=9, area_id=areas[3].id, expert_id=expertos[3].id,
                status="activa", confidence_level=0.88,
                user_explanation="Basado en experiencia: pedidos de alta prioridad retrasados más de 2h generan penalizaciones contractuales.",
                created_at=datetime.utcnow(),
            ),
            BusinessRuleModel(
                name="RN-002: División de pedido por falta de inventario",
                description="Si el inventario disponible es menor a la cantidad solicitada, dividir el pedido en entregas parciales.",
                conditions=[
                    {"field": "inventory_shortage", "operator": "eq", "value": True},
                ],
                suggested_action="Dividir el pedido en entregas parciales y coordinar reabastecimiento.",
                priority=8, area_id=areas[1].id, expert_id=expertos[1].id,
                status="activa", confidence_level=0.91,
                user_explanation="Regla validada: evita cancelaciones al comprometer solo el stock existente.",
                created_at=datetime.utcnow(),
            ),
            BusinessRuleModel(
                name="RN-003: Ruta alternativa por riesgo alto",
                description="Si la ruta tiene riesgo alto y existe una alternativa disponible, usar la ruta alternativa.",
                conditions=[
                    {"field": "route_risk", "operator": "eq", "value": "alto"},
                    {"field": "alternative_route_available", "operator": "eq", "value": True},
                ],
                suggested_action="Usar la ruta alternativa y documentar el motivo del desvío.",
                priority=7, area_id=areas[0].id, expert_id=expertos[0].id,
                status="activa", confidence_level=0.85,
                user_explanation="Rutas con riesgo alto han causado pérdidas de mercadería en el pasado.",
                created_at=datetime.utcnow(),
            ),
            BusinessRuleModel(
                name="RN-004: Escalamiento a gerencia por cliente estratégico",
                description="Si el cliente es estratégico y la probabilidad de retraso supera el 70%, escalar al gerente de área.",
                conditions=[
                    {"field": "client_type", "operator": "eq", "value": "estrategico"},
                    {"field": "delay_probability", "operator": "gt", "value": 70},
                ],
                suggested_action="Escalar inmediatamente al gerente de área y preparar plan de contingencia.",
                priority=10, area_id=areas[4].id, expert_id=expertos[4].id,
                status="activa", confidence_level=0.93,
                user_explanation="Clientes estratégicos representan el 60% de ingresos; cualquier falla requiere atención gerencial.",
                created_at=datetime.utcnow(),
            ),
            BusinessRuleModel(
                name="RN-005: Revisión automática por retroalimentación negativa",
                description="Si una regla acumula 3 o más calificaciones negativas en sus últimas 5 aplicaciones, marcarla para revisión.",
                conditions=[
                    {"field": "negative_feedback_count", "operator": "gte", "value": 3},
                ],
                suggested_action="Marcar la regla en estado 'en_revision' y notificar al administrador de conocimiento.",
                priority=6, area_id=areas[4].id, expert_id=expertos[4].id,
                status="activa", confidence_level=1.0,
                user_explanation="Regla de sistema interno para mantener la calidad del base de conocimiento.",
                created_at=datetime.utcnow(),
            ),
        ]
        db.add_all(reglas)
        db.commit()
        print("[Nexus-Corp] Seed completado: usuarios, expertos, áreas y reglas cargados.")
    except Exception as e:
        db.rollback()
        print(f"[Nexus-Corp] Error en seed: {e}")
    finally:
        db.close()
