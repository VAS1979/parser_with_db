""" Последовательно обрабатывает цепочку вызовов функций """

import aiohttp

from parser_with_db.src.requests import request_securities
from parser_with_db.src.test_response import check_response
from parser_with_db.src.type_column import create_column_typing
from parser_with_db.src.repositories import (create_db_tables,
                                             write_finished_data)


async def handle_call_chain(name_table, url, template):
    """ Обрабатывает цепочки вызовов """

    async with aiohttp.ClientSession() as session:
        response = await request_securities(session, url)

    await check_response(response, "req")

    securities_list = response["securities"]["data"]

    column_create = await create_column_typing(response, template)
    await create_db_tables(column_create[0], name_table)
    await write_finished_data(column_create[1], name_table,
                              securities_list)
