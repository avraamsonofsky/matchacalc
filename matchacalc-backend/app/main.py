from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.auth.routes import router as auth_router
from app.calc.routes import router as calc_router
from app.reports.routes import router as reports_router
from app.admin.routes import router as admin_router
from app.lots.routes import router as lots_router
from app.collections.routes import router as collections_router
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
app.include_router(lots_router, prefix="/api/v1/lots", tags=["lots"])
app.include_router(collections_router, prefix="/api/v1/collections", tags=["collections"])


@app.get("/")
def read_root():
    return {"message": "MatchaCalc API v0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/health")
def health_check_v1():
    return {"status": "ok"}


# Раздача статических файлов фронтенда (должно быть в конце, после всех API роутов)
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        # Раздача CSS, JS и других статических файлов
        app.mount("/css", StaticFiles(directory=str(static_dir / "css")), name="css")
        app.mount("/js", StaticFiles(directory=str(static_dir / "js")), name="js")
        
        # Раздача загруженных изображений
        uploads_dir = static_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    
    # Catch-all для HTML файлов (SPA routing)
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Раздача фронтенда для всех путей, кроме API"""
        # Если путь начинается с api/, не обрабатываем (должен вернуть 404 от FastAPI)
        if path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        
        # Специальная обработка для uploads
        if path.startswith("uploads/"):
            file_path = static_dir / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            raise HTTPException(status_code=404)
        
        file_path = static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Для всех остальных путей отдаём index.html (SPA)
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
