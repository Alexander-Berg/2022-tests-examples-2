from db.db import db_ydb
from settings.settings import logger
from functions.reserve_check_list import crypt


async def check_order(order_id: str, login: str) -> bool:
    try:
        res = [{'order_verification_rules': b'5'}]
        logger.info(f'check_order {res}')
        if res:
            rules = res[0]['order_verification_rules'].decode('UTF-8').split(', ')
            for i in rules:
                if len(order_id) == int(i):
                    return True
            return False
        else:
            return True

    except Exception as e:
        logger.error(f'check_order {e}')
        return True
