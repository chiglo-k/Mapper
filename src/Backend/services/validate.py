class Validator:
    @staticmethod
    def validate_data(data: list, required_fields: list = None):
        if not required_fields:
            required_fields = []

        errors = []

        for i, item in enumerate(data):
            item_errors = []

            # Проверка наличия обязательных полей
            for field in required_fields:
                if field not in item or item[field] is None or item[field] == "":
                    item_errors.append(f"Missing required field: {field}")

            if item_errors:
                errors.append({
                    "row": i,
                    "errors": item_errors
                })

        return len(errors) == 0, errors