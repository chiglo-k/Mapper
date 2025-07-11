import streamlit as st

from api_client import ApiClient
from project_manager import ProjectManager
from mapping_manager import MappingManager
from file_uploader import FileUploader
from data_processor import DataProcessor
from data_sender import DataSender
from config.config import config


# Основной класс приложения
class ApiManagerApp:
    def __init__(self, api_base_url=config['URL']['url_api']):
        # Настройка заголовка приложения
        st.set_page_config(page_title="API Manager", layout="wide")
        st.title("API Endpoint Manager")

        # Инициализация API клиента
        self.api_client = ApiClient(api_base_url)

        # Инициализация менеджеров
        self.project_manager = ProjectManager(self.api_client)
        self.mapping_manager = MappingManager(self.api_client)
        self.file_uploader = FileUploader(self.api_client)
        self.data_processor = DataProcessor(self.api_client)
        self.data_sender = DataSender(self.api_client)

    def run(self):
        # Создание боковой панели с навигацией
        st.sidebar.title("Навигация")
        page = st.sidebar.radio(
            "Выберите раздел:",
            ["Проекты", "Маппинг", "Загрузка файлов", "Обработка данных", "Отправка данных"]
        )

        # Запуск класса в зависимости от выбранной страницы
        if page == "Проекты":
            self.project_manager.render()
        elif page == "Маппинг":
            self.mapping_manager.render()
        elif page == "Загрузка файлов":
            self.file_uploader.render()
        elif page == "Обработка данных":
            self.data_processor.render()
        elif page == "Отправка данных":
            self.data_sender.render()