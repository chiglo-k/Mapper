from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json

from src.Backend.database.database import get_db
from src.Backend.models.project import Project_Data
from src.Backend.models.mapping import Mapping
from src.Backend.services.file_loader import FileLoader
from src.Backend.services.file_parser import FileParser
from src.Backend.services.mapper import Mapper
from src.Backend.services.validate import Validator
from src.Backend.services.data_send import DataSender


router = APIRouter()


@router.post("/projects/", response_model=dict)
def create_project(project: dict, db: Session = Depends(get_db)):
    # Создание проекта в базе данных
    db_project = Project_Data(
        name=project["name"],
        description=project.get("description", ""),
        api_key=str(uuid.uuid4())
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {
        "id": db_project.id,
        "name": db_project.name,
        "description": db_project.description,
        "api_key": db_project.api_key,
        "created_at": db_project.created_at
    }


@router.get("/projects/", response_model=List[dict])
def get_projects(db: Session = Depends(get_db)):
    # Просмотр всех активных проектов
    projects = db.query(Project_Data).filter(Project_Data.is_active == True).all()
    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at
        }
        for project in projects
    ]


@router.get("/projects/{project_id}", response_model=dict)
def get_project(project_id: int, db: Session = Depends(get_db)):
    # Просмотр конкретного проекта в базе данных
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "api_key": project.api_key,
        "created_at": project.created_at
    }


@router.post("/projects/{project_id}/mapping", response_model=dict)
def create_mapping_config(project_id: int, config: dict, db: Session = Depends(get_db)):
    # Проверка существования проекта
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Создание конфигурации маппинга
    db_config = Mapping(
        project_id=project_id,
        name=config["name"],
        source_format=config["source_format"],
        mapping_rules=config["mapping_rules"]
    )

    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return {
        "id": db_config.id,
        "name": db_config.name,
        "source_format": db_config.source_format,
        "mapping_rules": db_config.mapping_rules,
        "created_at": db_config.created_at
    }


@router.get("/projects/{project_id}/mapping", response_model=List[dict])
def get_mapping_configs(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Получение конфигураций маппинга для проекта
    configs = db.query(Mapping).filter(Mapping.project_id == project_id).all()

    return [
        {
            "id": config.id,
            "name": config.name,
            "source_format": config.source_format,
            "mapping_rules": config.mapping_rules,
            "created_at": config.created_at
        }
        for config in configs
    ]


@router.get("/projects/{project_id}/mapping/{config_id}", response_model=dict)
def get_mapping_config(project_id: int, config_id: int, db: Session = Depends(get_db)):
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Получение конкретной конфигурации маппинга
    config = db.query(Mapping).filter(
        Mapping.id == config_id,
        Mapping.project_id == project_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Mapping configuration not found")

    return {
        "id": config.id,
        "name": config.name,
        "source_format": config.source_format,
        "mapping_rules": config.mapping_rules,
        "created_at": config.created_at
    }


@router.post("/projects/{project_id}/upload-file", response_model=dict)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Загрузка содержимого файла
        content, filename = await FileLoader.load_from_upload(file)

        # Парсинг содержимого файла
        parsed_data = FileParser.parse_file(content, filename)

        return {
            "filename": filename,
            "record_count": len(parsed_data),
            "sample_data": parsed_data[:5] if len(parsed_data) > 5 else parsed_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/process-file", response_model=dict)
async def process_file(
    project_id: int,
    mapping_id: int = Form(...),
    file: UploadFile = File(...),
    required_fields: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):

    # Проверка существования проекта
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Проверка существования конфигурации маппинга
    mapping_config = db.query(Mapping).filter(
        Mapping.id == mapping_id,
        Mapping.project_id == project_id
    ).first()

    if not mapping_config:
        raise HTTPException(status_code=404, detail="Mapping configuration not found")

    try:
        # Парсинг обязательных полей
        req_fields = json.loads(required_fields) if required_fields else []

        # Загрузка содержимого файла
        content, filename = await FileLoader.load_from_upload(file)

        # Парсинг содержимого файла
        parsed_data = FileParser.parse_file(content, filename)

        # Применение маппинга
        mapped_data = Mapper.apply_mapping(parsed_data, mapping_config.mapping_rules)

        # Валидация данных
        is_valid, errors = Validator.validate_data(mapped_data, req_fields)

        return {
            "filename": filename,
            "record_count": len(mapped_data),
            "is_valid": is_valid,
            "validation_errors": errors,
            "sample_data": mapped_data[:5] if len(mapped_data) > 5 else mapped_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/send-data", response_model=dict)
async def send_data(
    project_id: int,
    data: List[dict],
    api_url: str = Form(...),
    db: Session = Depends(get_db)
):
    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Отправка данных через внешний API
        response = await DataSender.send_data(data, api_url, project.api_key)

        return {
            "success": True,
            "record_count": len(data),
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/process-and-send", response_model=dict)
async def process_and_send(
    project_id: int,
    mapping_id: int = Form(...),
    file: UploadFile = File(...),
    api_url: str = Form(...),
    required_fields: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):

    project = db.query(Project_Data).filter(Project_Data.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Проверка существования конфигурации маппинга
    mapping_config = db.query(Mapping).filter(
        Mapping.id == mapping_id,
        Mapping.project_id == project_id
    ).first()

    if not mapping_config:
        raise HTTPException(status_code=404, detail="Mapping configuration not found")

    try:
        # Парсинг обязательных полей
        req_fields = json.loads(required_fields) if required_fields else []

        # Загрузка файла
        content, filename = await FileLoader.load_from_upload(file)

        # Парсинг файла
        parsed_data = FileParser.parse_file(content, filename)

        # Применение маппинга
        mapped_data = Mapper.apply_mapping(parsed_data, mapping_config.mapping_rules)

        # Валидация данных
        is_valid, errors = Validator.validate_data(mapped_data, req_fields)

        if not is_valid:
            return {
                "success": False,
                "filename": filename,
                "validation_errors": errors
            }

        response = await DataSender.send_data(mapped_data, api_url, project.api_key)

        return {
            "success": True,
            "filename": filename,
            "record_count": len(mapped_data),
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))