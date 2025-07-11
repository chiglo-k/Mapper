import streamlit as st
import json
import pandas as pd


# Класс для управления маппинг процессом
class MappingManager:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("Конфигурации маппинга")

        # Вкладки для создания и просмотра маппингов
        mapping_tab1, mapping_tab2, mapping_tab3 = st.tabs(["Создать маппинг", "Список маппингов", "Детали маппинга"])

        # Получаем список проектов, если его еще нет
        if 'projects' not in st.session_state:
            projects = self.api_client.make_request("/api/projects/")
            if projects:
                st.session_state.projects = projects

        # Проверяем, есть ли проекты
        if 'projects' in st.session_state and len(st.session_state.projects) > 0:
            # Создаем выпадающий список с проектами
            project_names = [f"{p['id']} - {p['name']}" for p in st.session_state.projects]

            with mapping_tab1:
                self._render_create_mapping(project_names)

            with mapping_tab2:
                self._render_mapping_list(project_names)

            with mapping_tab3:
                self._render_mapping_details(project_names)
        else:
            st.warning("Нет доступных проектов. Создайте проект в разделе 'Проекты'.")

    def _render_create_mapping(self, project_names):
        st.subheader("Создать новую конфигурацию маппинга")

        selected_project = st.selectbox("Выберите проект", project_names, key="mapping_create_project")
        project_id = int(selected_project.split(" - ")[0])

        # Форма для создания маппинга
        with st.form("create_mapping_form"):
            mapping_name = st.text_input("Название маппинга")
            source_format = st.selectbox("Формат источника", ["CSV", "JSON", "XML", "Excel"])

            # Редактор правил маппинга (JSON)
            st.write("Правила маппинга (JSON):")
            mapping_rules = st.text_area("", value='{\n  "field1": "target_field1",\n  "field2": "target_field2"\n}')

            submit_button = st.form_submit_button("Создать маппинг")

            if submit_button:
                if mapping_name and mapping_rules:
                    try:
                        # Проверяем, что правила маппинга - JSON
                        rules_json = json.loads(mapping_rules)

                        mapping_data = {
                            "name": mapping_name,
                            "source_format": source_format,
                            "mapping_rules": rules_json
                        }

                        result = self.api_client.make_request(f"/api/projects/{project_id}/mapping", method="POST", data=mapping_data)

                        if result:
                            st.success(f"Маппинг '{mapping_name}' успешно создан!")
                            st.json(result)
                    except json.JSONDecodeError:
                        st.error("Правила маппинга должны быть в формате JSON")
                else:
                    st.error("Заполните все обязательные поля")

    def _render_mapping_list(self, project_names):
        st.subheader("Список конфигураций маппинга")

        selected_project = st.selectbox("Выберите проект", project_names, key="mapping_list_project")
        project_id = int(selected_project.split(" - ")[0])

        # Кнопка для обновления списка маппингов
        if st.button("Получить маппинги"):
            mappings = self.api_client.make_request(f"/api/projects/{project_id}/mapping")

            if mappings:
                if len(mappings) > 0:
                    # Создаем DataFrame для отображения маппингов
                    df = pd.DataFrame(mappings)
                    # Преобразуем mapping_rules в строку для отображения
                    df['mapping_rules'] = df['mapping_rules'].apply(lambda x: json.dumps(x, indent=2))
                    st.dataframe(df)

                    # Сохраняем список маппингов в session state
                    st.session_state.mappings = mappings
                else:
                    st.info("Маппинги не найдены. Создайте новый маппинг.")

    def _render_mapping_details(self, project_names):
        st.subheader("Детали маппинга")

        selected_project = st.selectbox("Выберите проект", project_names, key="mapping_detail_project")
        project_id = int(selected_project.split(" - ")[0])

        # Получаем маппинги для выбранного проекта
        if st.button("Загрузить маппинги"):
            mappings = self.api_client.make_request(f"/api/projects/{project_id}/mapping")

            if mappings and len(mappings) > 0:
                st.session_state.current_mappings = mappings
                st.success("Маппинги загружены")
            else:
                st.info("Маппинги не найдены для этого проекта")

        # Если маппинги загружены, показываем выпадающий список
        if 'current_mappings' in st.session_state and len(st.session_state.current_mappings) > 0:
            mapping_names = [f"{m['id']} - {m['name']}" for m in st.session_state.current_mappings]
            selected_mapping = st.selectbox("Выберите маппинг", mapping_names)

            if selected_mapping:
                # Извлекаем ID маппинга из выбранного значения
                mapping_id = int(selected_mapping.split(" - ")[0])

                # Кнопка для получения деталей маппинга
                if st.button("Получить детали маппинга"):
                    mapping_details = self.api_client.make_request(f"/api/projects/{project_id}/mapping/{mapping_id}")

                    if mapping_details:
                        # Отображаем детали маппинга
                        st.write("Основная информация:")
                        st.write(f"ID: {mapping_details['id']}")
                        st.write(f"Название: {mapping_details['name']}")
                        st.write(f"Формат источника: {mapping_details['source_format']}")
                        st.write(f"Дата создания: {mapping_details['created_at']}")

                        st.write("Правила маппинга:")
                        st.json(mapping_details['mapping_rules'])