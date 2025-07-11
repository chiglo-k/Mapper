class Mapper:
    @staticmethod
    def apply_mapping(data: list, mapping_rules):
        result = []

        # Проверка, что mapping_rules является словарем
        if not isinstance(mapping_rules, dict):
            print(f"mapping_rules is not a dict: {type(mapping_rules).__name__}")
            return []

        for item in data:
            mapped_item = {}

            # Проверка, что item является словарем
            if not isinstance(item, dict):
                print(f"Warning: Expected dict, got {type(item).__name__}. Item: {item}")
                continue

            for target_field, source_info in mapping_rules.items():
                # Проверка, что source_info является словарем или строкой
                if isinstance(source_info, dict):
                    source_field = source_info.get('field', '')
                    transform_type = source_info.get('transform', 'string')
                elif isinstance(source_info, str):
                    # Если source_info - строка, используем ее как имя поля
                    source_field = source_info
                    transform_type = 'string'
                else:
                    print(f"Warning: Unexpected type for source_info: {type(source_info).__name__}")
                    continue

                if source_field and source_field in item:
                    value = item[source_field]

                    # Применяем преобразование типа
                    if transform_type == 'integer':
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            value = 0
                    elif transform_type == 'float':
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                    elif transform_type == 'boolean':
                        if isinstance(value, str):
                            value = value.lower() in ('true', 'yes', '1')
                        else:
                            value = bool(value)
                    else:  # string
                        value = str(value) if value is not None else ""

                    mapped_item[target_field] = value
                else:
                    # Если поле отсутствует, устанавливаем значение по умолчанию
                    mapped_item[target_field] = None

            result.append(mapped_item)

        return result