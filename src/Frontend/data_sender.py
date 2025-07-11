import streamlit as st
import json


# Класс для отправки данных
class DataSender:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("Отправка данных")

        # Если список проектов не загружен, загружаем его
        if 'projects' not in st.session_state:
            projects = self.api_client.make_request("/api/projects/")
            if projects:
                st.session_state.projects = projects

        if 'projects' in st.session_state and len(st.session_state.projects) > 0:
            project_names = [f"{p['id']} - {p['name']}" for p in st.session_state.projects]
            selected_project = st.selectbox("Выберите проект", project_names)
            project_id = int(selected_project.split(" - ")[0])

            st.subheader("Отправка данных через API")

            # Два подхода: отправка ранее обработанных данных и обработка с последующей отправкой файла
            send_tab1, send_tab2 = st.tabs(["Отправка обработанных данных", "Обработка и отправка файла"])

            with send_tab1:
                self._render_send_processed_data(project_id)

            with send_tab2:
                self._render_process_and_send(project_id)
        else:
            st.warning("Нет доступных проектов. Создайте проект в разделе 'Проекты'.")

    def _render_send_processed_data(self, project_id):
        if 'processed_data' in st.session_state and 'sample_data' in st.session_state.processed_data:
            st.write("Используются ранее обработанные данные:")
            st.write(f"Файл: {st.session_state.processed_data['filename']}")
            st.write(f"Количество записей: {st.session_state.processed_data['record_count']}")

            with st.form("send_data_form"):
                api_url = st.text_input("URL API для отправки данных", "https://api.example.com/data")
                submit_button = st.form_submit_button("Отправить данные")

                if submit_button:
                    if api_url:
                        data = {
                            "data": st.session_state.processed_data['sample_data'],
                            "api_url": api_url
                        }
                        result = self.api_client.make_request(
                            f"/api/projects/{project_id}/send-data",
                            method="POST",
                            data=data
                        )

                        if result:
                            st.success("Данные успешно отправлены!")
                            st.json(result)
                    else:
                        st.error("URL API обязателен для заполнения")
        else:
            st.info("Сначала обработайте файл в разделе 'Обработка данных'")

    def _render_process_and_send(self, project_id):
        st.write("Обработка и отправка файла в одном шаге")

        # Загрузка маппингов для выбранного проекта
        mappings = self.api_client.make_request(f"/api/projects/{project_id}/mapping")
        if mappings and len(mappings) > 0:
            st.session_state.current_mappings = mappings
            st.success("Маппинги загружены")
        else:
            st.info("Маппинги не найдены для этого проекта")

        if 'current_mappings' in st.session_state and len(st.session_state.current_mappings) > 0:
            mapping_names = [f"{m['id']} - {m['name']}" for m in st.session_state.current_mappings]
            with st.form("process_and_send_form"):
                selected_mapping = st.selectbox("Выберите маппинг", mapping_names)
                mapping_id = int(selected_mapping.split(" - ")[0])
                uploaded_file = st.file_uploader("Выберите файл", type=["csv", "json", "xlsx", "xml"])
                api_url = st.text_input("URL API для отправки данных", "https://api.example.com/data")
                st.write("Обязательные поля (JSON массив):")
                required_fields = st.text_area("", value='["field1", "field2"]')
                submit_button = st.form_submit_button("Обработать и отправить")

                if submit_button:
                    if uploaded_file is None:
                        st.error("Пожалуйста, выберите файл для обработки и отправки")
                    elif not api_url:
                        st.error("URL API обязателен для заполнения")
                    else:
                        try:
                            json.loads(required_fields)
                            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            form_data = {
                                "mapping_id": mapping_id,
                                "api_url": api_url,
                                "required_fields": required_fields
                            }
                            result = self.api_client.make_request(
                                f"/api/projects/{project_id}/process-and-send",
                                method="POST",
                                data=form_data,
                                files=files
                            )
                            if result:
                                if result.get('success'):
                                    st.success("Файл успешно обработан и отправлен!")
                                    st.write(f"Имя файла: {result['filename']}")
                                    st.write(f"Количество записей: {result['record_count']}")
                                    st.write("Ответ API:")
                                    st.json(result['response'])
                                else:
                                    st.error("Ошибка при обработке или отправке файла")
                                    if 'validation_errors' in result:
                                        st.error("Ошибки валидации:")
                                        st.json(result['validation_errors'])
                        except json.JSONDecodeError:
                            st.error("Обязательные поля должны быть в формате JSON массива")
                        except Exception as e:
                            st.error(f"Ошибка: {str(e)}")