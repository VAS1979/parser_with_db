""" Создание типов колок таблицы """

from parser_with_db.src.config import CONVERT_TYPES, logger


async def create_column_typing(response, template):
    """ Создает строки с типизированными
    наименованиями колонок """

    list_of_columns = response["securities"]["columns"]
    example_for_definition = response["securities"]["data"][0]

    column_typing = ""
    finish_data = []

    try:
        for i, value in enumerate(example_for_definition):
            column_name = list_of_columns[i]
            column_type = CONVERT_TYPES[str(type(value))]
            temp_value = f"{column_name} {column_type}, "
            column_typing += temp_value
        column_typing = column_typing[0:-2]
        logger.info("Схема таблицы успешно создана")
    except (IndexError, KeyError, TypeError) as e:
        logger.error("Ошибка обработки данных в цикле: %s", e)
        return None, None

    finish_data.append(column_typing)
    finish_data.append(len(example_for_definition))

    try:
        if list_of_columns != template:
            logger.error("Схема таблицы не совпадает с шаблоном")
            return None
    except ValueError as e:
        logger.error("Ошибка проверки схемы таблицы: %s", e)
        return None, None

    return finish_data
