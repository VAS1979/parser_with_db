""" Запросы к базе данных """

import aiosqlite

from parser_with_db.src.config import logger, DB_PATH


async def create_db_tables(column_create, table_name):
    """ Создает базу, если ее нет, создает таблицу
    если ее нет, пересоздает если уже имеются """

    create_table = f"CREATE TABLE IF NOT EXISTS \
        {table_name} ({column_create})"
    try:
        async with aiosqlite.connect(DB_PATH) as db_connection:
            async with db_connection.cursor() as cursor:
                logger.info("Соединение для создания %s открыто", table_name)

                # Удаляет существующую таблицу
                await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                await db_connection.commit()

                # Создает новую таблицу
                await cursor.execute(create_table)
                await db_connection.commit()
                logger.info("Соединение для создания %s закрыто", table_name)
                logger.info("Таблица %s успешно создана.", table_name)
    except aiosqlite.Error as e:
        logger.error("Ошибка при создании/обновлении таблицы: %s", e)
    return None


async def write_finished_data(column_count, table_name, securities_list):
    """ Заполняет базу данных значениями из
    полученного ответа на запрос парсера """

    try:
        async with aiosqlite.connect(DB_PATH) as db_connection:
            async with db_connection.cursor() as cursor:

                insert_query = f"INSERT INTO {table_name} VALUES \
                    ({','.join(['?'] * column_count)})"

                await cursor.execute(f"DELETE FROM {table_name}")
                await db_connection.commit()

                for i in range(column_count):
                    await cursor.execute(insert_query, (securities_list[i]))
                await db_connection.commit()
                logger.info("Записи успешно добавлены в таблицу")

    except aiosqlite.Error:
        logger.error("Ошибка при подключении к базе данных")
