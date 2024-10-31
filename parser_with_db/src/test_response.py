""" Проверка ответов MOEX на корректность ключей словаря """

from parser_with_db.src.config import REQUEST_KEY, REQUIRED_KEYS, logger


async def _check_keys(res, fkey):
    """ Проверяет наличие обязательных ключей в словаре"""

    first_key = REQUEST_KEY[fkey]
    securities_data = res.get(first_key)
    if securities_data:
        for key in REQUIRED_KEYS:
            if key not in securities_data:
                mes = f"Ключ '{key}' не найден в словаре 'securities'."
                raise ValueError(mes)
        logger.info("Проверка json на корректность ключей успешна")
        return securities_data
    raise ValueError(f"Ключ {first_key} не найден в словаре.")


async def check_response(resp, key):
    """ Проверяет response ответы от
     MOEX на корректность ключей"""

    try:
        checked_response = await _check_keys(resp, key)
        return checked_response
    except KeyError as e:
        logger.error("Ошибка: %s", e)
        return

    except ValueError as e:
        logger.error("Ошибка: %s", e)
        return
