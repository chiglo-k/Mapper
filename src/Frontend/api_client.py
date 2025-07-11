import streamlit as st
import requests

from config.config import config


# Класс для работы с API
class ApiClient:
    def __init__(self, base_url=config['URL']['url_api']):
        self.base_url = base_url

    def make_request(self, endpoint, method="GET", data=None, files=None):
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                st.error(f"Ошибка API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Ошибка при выполнении запроса: {str(e)}")
            return None