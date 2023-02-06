"""
ТОЛЬКО ДЛЯ ТЕСТИНГА
"""
import json
from settings.settings import logger
from aiogram import types
from functions.get_state import get_state

async def update_db_data_message(user_request):
    try:
        if type(user_request) == types.Message:
            status = await get_state(user_request.chat.id)
        else:
            status = await get_state(user_request.message.chat.id)
        logger.info('status {}'.format(status))
        state_data = str(status[0]['state_data'])
        logger.info('state_data {}'.format(state_data))
        json_data = json.loads(state_data.replace("'", '"'))
        state = status[0]['state']
        logger.info('json_data {}'.format(json_data))
        return {'json_data': json_data, 'state': state}
    except Exception as e:
        logger.error(e)
