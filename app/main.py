from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import coils
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Severstal Coils API",
    description="API для управления складом рулонов металла",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(coils.router, prefix="/api/v1", tags=["coils"])
