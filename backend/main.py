# backend/main.py
# Punto de entrada de la API Nexus-Corp para DistribLog S.A.
# Registra todos los routers y ejecuta el seed de datos iniciales al arrancar.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.infrastructure.database.connection import engine
from backend.infrastructure.database.models import Base
from backend.presentation.routers.auth_router import router as auth_router
from backend.presentation.routers.experts_router import router as experts_router
from backend.presentation.routers.knowledge_areas_router import router as knowledge_areas_router
from backend.presentation.routers.rules_router import router as rules_router
from backend.presentation.routers.decisions_router import router as decisions_router
from backend.presentation.routers.whatif_router import router as whatif_router
from backend.presentation.routers.feedback_router import router as feedback_router
from backend.presentation.routers.kpis_router import router as kpis_router
from backend.presentation.routers.users_router import router as users_router
from backend.infrastructure.seed import run_seed

app = FastAPI(
    title="Nexus-Corp — KBDSS DistribLog S.A.",
    description="Sistema de Soporte a Decisiones Basado en Conocimiento para logística mayorista.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
for router in [
    auth_router, experts_router, knowledge_areas_router,
    rules_router, decisions_router, whatif_router,
    feedback_router, kpis_router, users_router,
]:
    app.include_router(router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    run_seed(engine)


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "sistema": "Nexus-Corp", "empresa": "DistribLog S.A."}
