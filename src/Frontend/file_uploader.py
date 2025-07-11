import streamlit as st


# Класс для загрузки файлов
class FileUploader:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("Загрузка файлов")

        # Получаем список проектов, если его еще нет
        if 'projects' not in st.session_state:
            projects = self.api_client.make_request("/api/projects/")
            if projects:
                st.session_state.projects = projects

        # Проверяем, есть ли проекты
        if 'projects' in st.session_state and len(st.session_state.projects) > 0:
            # Создаем выпадающий список с проектами
            project_names = [f"{p['id']} - {p['name']}" for p in st.session_state.projects]
            selected_project = st.selectbox("Выберите проект", project_names)
            project_id = int(selected_project.split(" - ")[0])

            # Вкладки для разных способов загрузки файлов
            upload_tab1, upload_tab2, upload_tab3 = st.tabs(["Загрузка с локального диска", "Загрузка из S3", "Загрузка через API"])

            with upload_tab1:
                self._render_local_upload(project_id)

            with upload_tab2:
                self._render_s3_upload(project_id)

            with upload_tab3:
                self._render_api_upload(project_id)
        else:
            st.warning("Нет доступных проектов. Создайте проект в разделе 'Проекты'.")

    def _render_local_upload(self, project_id):
        st.subheader("Загрузка файла с локального диска")

        uploaded_file = st.file_uploader("Выберите файл для загрузки", type=["csv", "json", "xlsx", "xml"])

        if uploaded_file is not None:
            # Отображаем информацию о файле
            file_details = {"Имя файла": uploaded_file.name, "Тип файла": uploaded_file.type, "Размер": uploaded_file.size}
            st.write(file_details)

            # Кнопка для загрузки файла на сервер
            if st.button("Загрузить файл"):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

                result = self.api_client.make_request(f"/api/projects/{project_id}/upload-file", method="POST", files=files)

                if result:
                    st.success("Файл успешно загружен и обработан!")

                    # Отображаем информацию о загруженном файле
                    st.write(f"Имя файла: {result['filename']}")
                    st.write(f"Количество записей: {result['record_count']}")

                    # Отображаем примеры данных
                    st.subheader("Примеры данных:")
                    st.json(result['sample_data'])

                    # Сохраняем результат в session state для использования в других разделах
                    st.session_state.uploaded_file_data = result

    def _render_s3_upload(self, project_id):
        st.subheader("Загрузка файла из S3")

        with st.form("s3_upload_form"):
            bucket = st.text_input("Имя бакета S3")
            file_key = st.text_input("Ключ файла в S3")
            access_key = st.text_input("Access Key")
            secret_key = st.text_input("Secret Key", type="password")

            submit_button = st.form_submit_button("Загрузить файл из S3")

            if submit_button:
                if bucket and file_key and access_key and secret_key:
                    try:
                        # Загружаем файл из S3
                        content, filename = self.api_client.make_request(
                            f"/api/projects/{project_id}/upload-file-from-s3",
                            method="POST",
                            data={
                                "bucket": bucket,
                                "file_key": file_key,
                                "access_key": access_key,
                                "secret_key": secret_key
                            }
                        )

                        if content and filename:
                            st.success(f"Файл {filename} успешно загружен из S3 и обработан!")

                            # Отображаем информацию о загруженном файле
                            st.write(f"Имя файла: {filename}")
                            st.write(f"Количество записей: {len(content)}")

                            # Отображаем примеры данных
                            st.subheader("Примеры данных:")
                            st.json(content[:5])

                            # Сохраняем результат в session state для использования в других разделах
                            st.session_state.uploaded_file_data = {
                                "filename": filename,
                                "content": content
                            }
                    except Exception as e:
                        st.error(f"Ошибка при загрузке файла из S3: {str(e)}")
                else:
                    st.warning("Все поля должны быть заполнены для загрузки файла из S3")

    def _render_api_upload(self, project_id):
        st.subheader("Загрузка файла через API")

        with st.form("api_upload_form"):
            api_url = st.text_input("URL API для загрузки файла")
            submit_button = st.form_submit_button("Загрузить файл через API")

            if submit_button:
                if api_url:
                    try:
                        # Загружаем файл через API
                        response = self.api_client.make_request(
                            f"/api/projects/{project_id}/upload-file-from-api",
                            method="POST",
                            data={"api_url": api_url}
                        )

                        if response:
                            st.success(f"Файл успешно загружен через API и обработан!")

                            # Отображаем информацию о загруженном файле
                            st.write(f"Имя файла: {response['filename']}")
                            st.write(f"Количество записей: {response['record_count']}")

                            # Отображаем примеры данных
                            st.subheader("Примеры данных:")
                            st.json(response['sample_data'])

                            # Сохраняем результат в session state для использования в других разделах
                            st.session_state.uploaded_file_data = response
                    except Exception as e:
                        st.error(f"Ошибка при загрузке файла через API: {str(e)}")
                else:
                    st.warning("URL API должен быть указан для загрузки файла")