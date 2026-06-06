# tests/integration/test_api.py
# Pruebas de integración de endpoints críticos usando TestClient con BD SQLite en memoria.
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.database.models import Base
from backend.infrastructure.database.connection import get_db
from backend.infrastructure.seed import run_seed
from backend.main import app

# BD en memoria para pruebas
TEST_DATABASE_URL = "sqlite:///./test_nexus.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=test_engine)
    run_seed(test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def admin_token(client):
    resp = client.post("/api/v1/auth/login", data={
        "username": "admin@nexuscorp.com", "password": "Admin2026!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def decisor_token(client):
    resp = client.post("/api/v1/auth/login", data={
        "username": "decisor@nexuscorp.com", "password": "Decisor2026!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


class TestAuth:
    def test_login_admin_success(self, client):
        resp = client.post("/api/v1/auth/login", data={
            "username": "admin@nexuscorp.com", "password": "Admin2026!"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["role"] == "system_admin"

    def test_login_wrong_password(self, client):
        resp = client.post("/api/v1/auth/login", data={
            "username": "admin@nexuscorp.com", "password": "wrong"
        })
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = client.post("/api/v1/auth/login", data={
            "username": "noexiste@nexuscorp.com", "password": "Admin2026!"
        })
        assert resp.status_code == 401


class TestRules:
    def test_list_rules_requires_auth(self, client):
        resp = client.get("/api/v1/rules")
        assert resp.status_code == 401

    def test_list_rules_authenticated(self, client, admin_token):
        resp = client.get("/api/v1/rules", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 5

    def test_create_rule_as_admin(self, client, admin_token):
        payload = {
            "name": "RN-TEST: Regla de prueba",
            "description": "Regla creada en prueba de integración.",
            "conditions": [{"field": "x", "operator": "eq", "value": 1}],
            "suggested_action": "Acción de prueba",
            "priority": 4,
            "area_id": 1,
            "expert_id": 1,
            "confidence_level": 0.75,
        }
        resp = client.post("/api/v1/rules", json=payload,
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "pendiente"

    def test_create_rule_forbidden_for_decisor(self, client, decisor_token):
        payload = {
            "name": "RN-TEST-2",
            "description": "Intento no autorizado.",
            "conditions": [{"field": "x", "operator": "eq", "value": 1}],
            "suggested_action": "Acción",
            "priority": 1, "area_id": 1, "expert_id": 1,
        }
        resp = client.post("/api/v1/rules", json=payload,
                           headers={"Authorization": f"Bearer {decisor_token}"})
        assert resp.status_code == 403


class TestEvaluate:
    def test_evaluate_rn001(self, client, decisor_token):
        payload = {
            "input_data": {"order_priority": "alta", "delay_minutes": 150},
            "request_type": "logistica"
        }
        resp = client.post("/api/v1/decisions/evaluate", json=payload,
                           headers={"Authorization": f"Bearer {decisor_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "activated_rules" in data
        rule_names = [r["rule_name"] for r in data["activated_rules"]]
        assert any("RN-001" in name for name in rule_names)

    def test_evaluate_no_rules_match(self, client, decisor_token):
        payload = {
            "input_data": {"campo_raro": "valor_raro"},
            "request_type": "logistica"
        }
        resp = client.post("/api/v1/decisions/evaluate", json=payload,
                           headers={"Authorization": f"Bearer {decisor_token}"})
        assert resp.status_code == 200
        assert resp.json()["activated_rules"] == []

    def test_evaluate_requires_auth(self, client):
        resp = client.post("/api/v1/decisions/evaluate", json={"input_data": {}})
        assert resp.status_code == 401
