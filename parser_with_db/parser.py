""" Создание и заполнение базы данных парсером"""

import asyncio
import aiosqlite
import aiohttp

from parser_with_db.src.config import (PERIOD_BETWEEN_REQUEST, logger,
                                       SHARE_SBER_URL, TYPES_SECURITIES)
from parser_with_db.src.requests import request_share_sber
from parser_with_db.src.processor import handle_call_chain

# Остановка приложения через Ctrl+C
stop_event = asyncio.Event()


async def main():
    """Обрабатывает цикл вызовов
    обработчика запросов """

    try:
        await request_share_sber(SHARE_SBER_URL)
    except (aiohttp.ClientError, IndexError, KeyError,
            TypeError, ValueError, aiosqlite.Error) as s:
        logger.error("Ошибка запроса тестовой цены, %s", s)
    else:
        for name_table, url, template in TYPES_SECURITIES:
            try:
                await handle_call_chain(name_table, url, template)
            except (aiohttp.ClientError, IndexError, KeyError,
                    TypeError, ValueError, aiosqlite.Error, AttributeError):
                logger.error("Ошибка выполнения процесса")
            finally:
                logger.info("Цикл обработки запроса и записи в БД завершен\n")

    await asyncio.sleep(PERIOD_BETWEEN_REQUEST)


if __name__ == "__main__":
    while not stop_event.is_set():
        try:
            asyncio.run(main())
        except (aiohttp.ClientError, IndexError, KeyError,
                TypeError, ValueError, aiosqlite.Error, AttributeError):
            logger.error("Ошибка выполнения процесса")
        except KeyboardInterrupt:
            logger.info("Принудительная остановка программы пользователем")
            break
