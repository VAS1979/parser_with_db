""" Создание и заполнение базы данных парсером"""

import os
import asyncio
import logging
import aiosqlite
import aiohttp

# путь к базе данных
DB_PATH = os.path.join(os.path.dirname(__file__), "data_db.db")

# период между опросами парсера в секундах
PERIOD_BETWEEN_REQUEST = 36

# настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# адрес запроса к MOEX по корпоративным облигациям
CORPORATE_BOND_URL = ("https://iss.moex.com/iss/engines/stock/markets/bonds/"
                      "boards/TQCB/securities.json?iss.meta=off")
# адрес запроса к MOEX по ОФЗ
OFZ_BOND_URL = ("https://iss.moex.com/iss/engines/stock/markets/bonds/boards"
                "/TQOB/securities.json?iss.meta=off")

# словарь приведения соответствия типов данных
convert_types = {
    "<class 'str'>": "TEXT",
    "<class 'float'>": "REAL",
    "<class 'int'>": "INTEGER",
    "<class 'NoneType'>": "NUMERIC"
        }

# Названия таблиц в базе данных
OFZ_BONDS = "ofz_bonds"
CORP_BONDS = "corp_bonds"

# Шаблон для проверки изменений типов и наименований столбцов таблицы
BOND_COLUMN_TEMPLATE = [
    'SECID', 'BOARDID', 'SHORTNAME', 'PREVWAPRICE',
    'YIELDATPREVWAPRICE', 'COUPONVALUE', 'NEXTCOUPON', 'ACCRUEDINT',
    'PREVPRICE', 'LOTSIZE', 'FACEVALUE', 'BOARDNAME', 'STATUS', 'MATDATE',
    'DECIMALS', 'COUPONPERIOD', 'ISSUESIZE', 'PREVLEGALCLOSEPRICE',
    'PREVDATE', 'SECNAME', 'REMARKS', 'MARKETCODE', 'INSTRID', 'SECTORID',
    'MINSTEP', 'FACEUNIT', 'BUYBACKPRICE', 'BUYBACKDATE', 'ISIN', 'LATNAME',
    'REGNUMBER', 'CURRENCYID', 'ISSUESIZEPLACED', 'LISTLEVEL', 'SECTYPE',
    'COUPONPERCENT', 'OFFERDATE', 'SETTLEDATE', 'LOTVALUE',
    'FACEVALUEONSETTLEDATE'
    ]

# список соответствий названий таблиц и адресов шлюзов
TYPES_SECURITIES = [[OFZ_BONDS, OFZ_BOND_URL],
                    [CORP_BONDS, CORPORATE_BOND_URL]]


async def request_securities(url):
    """ Запрос к MOEX """

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                content = await resp.json(content_type=None)
        logger.info("Запрос парсера успешно выполнен")
        return content
    except aiohttp.ClientError as e:
        logger.error("Ошибка выполнения запроса: %s", e)
        return None


async def create_column_typing(response):
    """ Создает строки с типизированными
    наименованиями колонок """

    list_of_columns = response["securities"]["columns"]
    example_for_definition = response["securities"]["data"][0]

    column_typing = ""
    finish_data = []

    try:
        for i, value in enumerate(example_for_definition):
            column_name = list_of_columns[i]
            column_type = convert_types[str(type(value))]
            temp_value = f"{column_name} {column_type}, "
            column_typing += temp_value
        column_typing = column_typing[0:-2]
        logger.info("Схема таблицы успешно создана")
    except (IndexError, KeyError, TypeError) as e:
        logger.error("Ошибка обработки данных в цикле: %s", e)
        return None, None

    finish_data.append(column_typing)
    finish_data.append(len(example_for_definition))

    if list_of_columns != BOND_COLUMN_TEMPLATE:
        error_message = "Схема таблицы не совпадает с шаблоном:\n"
        error_message += f"Текущая схема: {list_of_columns}\n"
        error_message += f"Шаблон схемы: {BOND_COLUMN_TEMPLATE}"
        raise ValueError(error_message)

    return finish_data


async def create_db_tables(column_create, table_name):
    """ Создает базу, если ее нет, создает таблицу
    если ее нет, пересоздает если уже имеются """

    create_table = f"CREATE TABLE IF NOT EXISTS \
        {table_name} ({column_create})"
    try:
        async with aiosqlite.connect("data_db.db") as db_connection:
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


async def writing_finished_data(column_count, table_name, securities_list):
    """ Заполняет базу данных значениями из
    полученного ответа на запрос парсера """

    try:
        async with aiosqlite.connect("data_db.db") as db_connection:
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


async def processing(name_table, url):
    """ Обработка цепочки вызовов """

    response = await request_securities(url)
    securities_list = response["securities"]["data"]
    if response is None:
        logger.error("Ошибка получения данных от MOEX")
    else:
        column_create = await create_column_typing(response)
        if column_create is None:
            logger.error("Не удалось создать схему таблицы.")
        else:
            await create_db_tables(column_create[0], name_table)
            if create_db_tables is None:
                logger.error("Не удалось создать таблицу.")
            else:
                await writing_finished_data(column_create[1], name_table,
                                            securities_list)


async def main():
    """ Главная обработка цепочки вызовов """

    for name_table, url in TYPES_SECURITIES:
        await processing(name_table, url)

    await asyncio.sleep(PERIOD_BETWEEN_REQUEST)


while True:
    asyncio.run(main())
