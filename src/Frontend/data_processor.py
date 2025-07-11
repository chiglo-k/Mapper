# data_processor.py
import streamlit as st
import json


class DataProcessor:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("Обработка данных")

        # Получаем список проектов
        if 'projects' not in st.session_state:
            projects = self.api_client.make_request("/api/projects/")
            if projects:
                st.session_state.projects = projects

        if 'projects' in st.session_state and len(st.session_state.projects) > 0:
            # Выбор проекта
            project_names = [f"{p['id']} - {p['name']}" for p in st.session_state.projects]
            selected_project = st.selectbox("Выберите проект", project_names)
            project_id = int(selected_project.split(" - ")[0])

            # Загружаем маппинги для выбранного проекта
            mappings = self.api_client.make_request(f"/api/projects/{project_id}/mapping")
            if mappings and len(mappings) > 0:
                st.session_state.current_mappings = mappings
                st.success("Маппинги загружены")
            else:
                st.info("Маппинги не найдены для этого проекта")

            # Если маппинги доступны, показываем форму обработки файла
            if 'current_mappings' in st.session_state and len(st.session_state.current_mappings) > 0:
                mapping_names = [f"{m['id']} - {m['name']}" for m in st.session_state.current_mappings]

                # Проверяем, есть ли загруженный файл
                file_available = 'uploaded_file_data' in st.session_state

                if file_available:
                    st.success(f"Найден загруженный файл: {st.session_state.uploaded_file_data['filename']}")
                else:
                    st.warning("Файл не загружен. Пожалуйста, загрузите файл в разделе 'Загрузка файлов'.")

                # Выбор маппинга
                selected_mapping = st.selectbox("Выберите маппинг", mapping_names)
                mapping_id = int(selected_mapping.split(" - ")[0])

                # Получаем детали выбранного маппинга
                selected_mapping_details = None
                for mapping in st.session_state.current_mappings:
                    if mapping['id'] == mapping_id:
                        selected_mapping_details = mapping
                        break

                # Если нашли детали маппинга, показываем правила
                if selected_mapping_details and 'mapping_rules' in selected_mapping_details:
                    st.subheader("Правила маппинга")
                    st.json(selected_mapping_details['mapping_rules'])

                # Кнопка для обработки файла
                if file_available and st.button("Обработать файл с использованием выбранного маппинга"):
                    try:
                        # Отправляем запрос на обработку файла с использованием ID файла и ID маппинга
                        result = self.api_client.make_request(
                            f"/api/projects/{project_id}/process-uploaded-file",
                            method="POST",
                            data={
                                "file_id": st.session_state.uploaded_file_data['id'],
                                "mapping_id": mapping_id
                            }
                        )

                        if result:
                            st.success("Файл успешно обработан!")
                            st.write(f"Имя файла: {result['filename']}")
                            st.write(f"Количество записей: {result['record_count']}")
                            st.write(f"Валидация: {'Успешно' if result['is_valid'] else 'Ошибка'}")

                            if not result['is_valid'] and 'validation_errors' in result:
                                st.error("Ошибки валидации:")
                                st.json(result['validation_errors'])

                            st.subheader("Примеры обработанных данных:")
                            st.json(result['sample_data'])

                            # Сохраняем результат в session state для использования в других разделах
                            st.session_state.processed_data = result
                    except Exception as e:
                        st.error(f"Ошибка при обработке файла: {str(e)}")
            else:
                st.warning("Для выбранного проекта нет доступных маппингов. Создайте маппинг в разделе 'Маппинг'.")
        else:
            st.warning("Нет доступных проектов. Создайте проект в разделе 'Проекты'.")