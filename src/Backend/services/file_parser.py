import pandas as pd
import json
import io
from fastapi import HTTPException
import csv


class FileParser:

    @staticmethod
    def parse_file(content: bytes, filename: str):
        file_extension = filename.split('.')[-1].lower()

        try:
            if file_extension == 'csv':
                return FileParser._parse_csv(content)
            elif file_extension == 'xlsx':
                return FileParser._parse_xlsx(content)
            elif file_extension == 'json':
                return FileParser._parse_json(content)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    @staticmethod
    def _parse_csv(content: bytes):
        try:
            # Декодирование содержимого в строку
            text_content = content.decode('utf-8', errors='replace')

            # Удаление BOM, если он есть
            if text_content.startswith('\ufeff'):
                text_content = text_content[1:]

            # Определение разделителя
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text_content)
            delimiter = dialect.delimiter

            # Разделение на строки
            lines = text_content.splitlines()
            if not lines:
                return []

            # Получение заголовков из первой строки
            headers = [h.strip() for h in lines[0].split(delimiter)]

            # Обработка данных
            result = []
            for line in lines[1:]:
                if not line.strip():
                    continue

                values = line.split(delimiter)

                # Если количество значений не соответствует количеству заголовков,
                # пропускаем строку или дополняем недостающие значения
                if len(values) < len(headers):
                    values.extend([''] * (len(headers) - len(values)))
                elif len(values) > len(headers):
                    values = values[:len(headers)]

                # Создание словаря для строки
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(values):
                        row_dict[header.strip()] = values[i].strip()
                    else:
                        row_dict[header.strip()] = ''

                result.append(row_dict)

            return result
        except Exception as e:
            print(f"Error parsing CSV: {str(e)}")
            raise Exception(f"Failed to parse CSV file: {str(e)}")

    @staticmethod
    def _parse_xlsx(content: bytes):
        df = pd.read_excel(io.BytesIO(content))
        return df.to_dict(orient='records')

    @staticmethod
    def _parse_json(content: bytes):
        data = json.loads(content.decode('utf-8'))
        # Проверяем, является ли JSON массивом объектов
        if isinstance(data, list):
            return data
        else:
            # Если это один объект или другая структура, преобразуем в список
            return [data]