"""
ТОЛЬКО ДЛЯ ТЕСТИНГА
"""
from db.db import db_ydb
from settings.settings import logger

db = db_ydb()

state_db = {
    "chat_id": "000000",
    "state": "",
    "state_data": {

    }
}


async def update_state(chat_id: str, state: str, state_data: dict) -> str:
    state_db.update(chat_id=chat_id, state=state, state_data=state_data)
    logger.info('state_db update {}'.format(state_db))
    return 'state_db ok'


async def get_state(chat_id: str) -> list:
    return [state_db]
