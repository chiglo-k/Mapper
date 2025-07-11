from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
from dataclasses import dataclass
from datetime import datetime
import logging

from src.Backend.config.confg import config


Base = declarative_base()

@dataclass
class DBConnector:
    """Класс для подключения к Базе данных"""

    engine = None
    SessionLocal = None

    def __post_init__(self):
        self._initialize_database()
        self._setup_logging()


    def _setup_logging(self):
        """Конфиг логирования"""
        logging.basicConfig(
            level=logging.INFO,
            filename="Log.txt",
            filemode="a",
            format="%(asctime)s %(levelname)s %(message)s"
        )
        logging.info(f"Начало сессии: {datetime.now()}")

    def _initialize_database(self):
        """
        Инициализация подключения к БД
        """
        self.engine = create_engine(
            config['SQL']['db_dta'],
        )
        self.SessionLocal = sessionmaker(
            autoflush=False,
            bind=self.engine
        )
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def _get_session(self)-> Generator:
        """Подключение к БД"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as ConnectionError:
            session.rollback()
            logging.error("Проверьте доступ (данные доступа) к БД")
            raise ConnectionError
        finally:
            session.close()

    def session_start(self):
        return self._get_session()


db_connector = DBConnector() ## Доступ для API
def get_db():
    with db_connector.session_start() as session:
        yield session


if __name__ == "__main__":
    try:
        db_cn = DBConnector()
        db_cn.session_start()
    except:
        logging.error("Проверьте доступ (данные доступа) к БД")
    finally:
        logging.info(f"Сессия окончена: {datetime.now()}")