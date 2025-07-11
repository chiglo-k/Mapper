import streamlit as st
import pandas as pd


# Класс для управления проектами
class ProjectManager:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("Управление проектами")

        # Вкладки для создания и просмотра проектов
        project_tab1, project_tab2, project_tab3 = st.tabs(["Создать проект", "Список проектов", "Детали проекта"])

        with project_tab1:
            self._render_create_project()

        with project_tab2:
            self._render_project_list()

        with project_tab3:
            self._render_project_details()

    def _render_create_project(self):
        st.subheader("Создать новый проект")

        # Форма для создания проекта
        with st.form("create_project_form"):
            project_name = st.text_input("Название проекта")
            project_description = st.text_area("Описание проекта")
            submit_button = st.form_submit_button("Создать проект")

            if submit_button:
                if project_name:
                    project_data = {
                        "name": project_name,
                        "description": project_description
                    }

                    result = self.api_client.make_request("/api/projects/", method="POST", data=project_data)

                    if result:
                        st.success(f"Проект '{project_name}' успешно создан!")
                        st.json(result)
                else:
                    st.error("Название проекта обязательно для заполнения")

    def _render_project_list(self):
        st.subheader("Список проектов")

        # Кнопка для обновления списка проектов
        if st.button("Обновить список проектов"):
            projects = self.api_client.make_request("/api/projects/")

            if projects:
                if len(projects) > 0:
                    # Создаем DataFrame для отображения проектов
                    df = pd.DataFrame(projects)
                    st.dataframe(df)

                    # Сохраняем список проектов в session state для использования в других вкладках
                    st.session_state.projects = projects
                else:
                    st.info("Проекты не найдены. Создайте новый проект.")

    def _render_project_details(self):
        st.subheader("Детали проекта")

        # Получаем список проектов из session state или делаем запрос
        if 'projects' not in st.session_state:
            projects = self.api_client.make_request("/api/projects/")
            if projects:
                st.session_state.projects = projects

        if 'projects' in st.session_state and len(st.session_state.projects) > 0:
            # Создаем выпадающий список с проектами
            project_names = [f"{p['id']} - {p['name']}" for p in st.session_state.projects]
            selected_project = st.selectbox("Выберите проект", project_names)

            if selected_project:
                # Извлекаем ID проекта из выбранного значения
                project_id = int(selected_project.split(" - ")[0])

                # Кнопка для получения деталей проекта
                if st.button("Получить детали проекта"):
                    project_details = self.api_client.make_request(f"/api/projects/{project_id}")

                    if project_details:
                        st.json(project_details)
        else:
            st.info("Нет доступных проектов. Создайте новый проект или обновите список.")
