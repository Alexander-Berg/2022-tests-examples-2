from db.db import db_ydb
from settings.settings import logger
from aiogram import types
from functions.personal_entity_id import pd

db = db_ydb()


async def check_white_list(user_request) -> bool:
    white_list = [{'pd_login_id': b'0a8d3a2f66fd4f89bc8a484da2332f10'}]
    # white_list = []
    logger.info(user_request)
    if white_list:
        return True
    else:
        return False
