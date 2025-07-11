import logging
from sqlalchemy import text
from src.Backend.database.database import Base, db_connector
from src.Backend.models.project import Project_Data
from src.Backend.models.mapping import Mapping

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Подключение к базе данных
    engine = db_connector.engine

    # Удаление существующих таблиц
    logger.info("Удаление существующих таблиц...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Таблицы успешно удалены")

    # Создание таблиц заново
    logger.info("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы успешно созданы")

    print("Таблицы успешно пересозданы!")
except Exception as e:
    logger.error(f"Ошибка при пересоздании таблиц: {str(e)}")