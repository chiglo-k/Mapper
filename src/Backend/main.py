from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.Backend.endpoint import api_endpoints

app = FastAPI(
    title="Mapper Service",
    description="API для управления проектами маппинга данных",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # доступ со всех источников
    allow_credentials=True,
    allow_methods=["*"], # доступ всех методов, включая ~HTTP~!!
    allow_headers=["*"],
)


app.include_router(api_endpoints.router, prefix="/api", tags=["projects"]) # присоединение эндпоинтов с endpoint/api_endpoints


@app.get("/")
async def root():
    return {"Добро пожаловать в API Mapping Project. Документация доступна по адресу /docs"}
