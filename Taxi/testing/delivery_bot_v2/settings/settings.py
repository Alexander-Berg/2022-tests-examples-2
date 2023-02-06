"""
ТОЛЬКО ДЛЯ ТЕСТИНГА
"""
import logging
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import suptech

rtc = suptech.Rtc('delivery_sup_bot_testing', ident='yandex-taxi-suptech-bot')
TOKENS = rtc.tokens()
rtc.init_logger()
token = ''
tracker = suptech.Tracker(token=TOKENS['B2B_TRACKER'], org_id='650580')
YT_TOKEN = TOKENS['YT_TOKEN']
logging.basicConfig(level='INFO')
logger = logging.getLogger('delivery_sup_bot_testing')
