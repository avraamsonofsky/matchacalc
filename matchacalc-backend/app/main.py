from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.calc.routes import router as calc_router
from app.reports.routes import router as reports_router
from app.admin.routes import router as admin_router
from app.ratelimit.middleware import RateLimitMiddleware

app = FastAPI(
    title="MatchaCalc",
    version="0.1.0",
    description="Калькулятор доходности коммерческой недвижимости"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Роутеры
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(calc_router, prefix="/api/v1/calc", tags=["calc"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
def read_root():
    return {"message": "MatchaCalc API v0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/health")
def health_check_v1():
    return {"status": "ok"}
