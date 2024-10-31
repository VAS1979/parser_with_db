""" Модуль конфигурации """

import logging

# путь к базе данных
DB_PATH = "db/data_db.db"

# период между опросами парсера в секундах
PERIOD_BETWEEN_REQUEST = 27

# настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# адрес запроса к MOEX по корпоративным облигациям
CORPORATE_BOND_URL = ("https://iss.moex.com/iss/engines/stock/markets/bonds/"
                      "boards/TQCB/securities.json?iss.meta=off")
# адрес запроса к MOEX по ОФЗ
OFZ_BOND_URL = ("https://iss.moex.com/iss/engines/stock/markets/bonds/boards"
                "/TQOB/securities.json?iss.meta=off")

# адрес запроса к MOEX по акциям
SHARE_URL = ("http://iss.moex.com/iss/engines/stock/markets/shares/boards/"
             "TQBR/securities.json?iss.meta=off")

# адрес запроса по акции SBER (для тестирования работы MOEX)
SHARE_SBER_URL = ("http://iss.moex.com/iss/engines/stock/markets/"
                  "shares/boards/TQBR/securities/SBER.json?"
                  "iss.meta=off&iss.only=marketdata&marketdata."
                  "columns=SECID,LAST")

# словарь приведения соответствия типов данных
CONVERT_TYPES = {
    "<class 'str'>": "TEXT",
    "<class 'float'>": "REAL",
    "<class 'int'>": "INTEGER",
    "<class 'NoneType'>": "NUMERIC"
        }

# Названия таблиц в базе данных
OFZ_BONDS = "ofz_bonds"
CORP_BONDS = "corp_bonds"
SHARES = "shares"

# Шаблон для проверки изменений типов и наименований столбцов таблицы облигаций
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

# Шаблон для проверки изменений типов и наименований столбцов таблицы акций
SHARES_COLUMN_TEMPLATE = [
    'SECID', 'BOARDID', 'SHORTNAME', 'PREVPRICE', 'LOTSIZE', 'FACEVALUE',
    'STATUS', 'BOARDNAME', 'DECIMALS', 'SECNAME', 'REMARKS', 'MARKETCODE',
    'INSTRID', 'SECTORID', 'MINSTEP', 'PREVWAPRICE', 'FACEUNIT', 'PREVDATE',
    'ISSUESIZE', 'ISIN', 'LATNAME', 'REGNUMBER', 'PREVLEGALCLOSEPRICE',
    'CURRENCYID', 'SECTYPE', 'LISTLEVEL', 'SETTLEDATE'
    ]

# список соответствий названий таблиц и адресов шлюзов
TYPES_SECURITIES = [[OFZ_BONDS, OFZ_BOND_URL, BOND_COLUMN_TEMPLATE],
                    [CORP_BONDS, CORPORATE_BOND_URL, BOND_COLUMN_TEMPLATE],
                    [SHARES, SHARE_URL, SHARES_COLUMN_TEMPLATE]]

# список колонок во вложенном словаре json ответе MOEX
# допустимые структуры ответа:
# {"marketdata": {"columns": [], "data": []} изолированный запрос по SBER
# {"securities": {"columns": [], "data": []} запрос по всем бумагам
REQUIRED_KEYS = ["columns", "data"]

# словарь первичных ключей в json ответе MOEX
REQUEST_KEY = {"check": "marketdata", "req": "securities"}
