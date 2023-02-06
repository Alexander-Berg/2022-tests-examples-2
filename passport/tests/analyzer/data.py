# -*- coding: utf-8 -*-

from passport.backend.core.historydb.analyzer.event_handlers.question_answer import MAX_HINTQ_HINTA_TS_OFFSET
from passport.backend.utils.time import (
    datetime_to_unixtime,
    parse_datetime,
)


TEST_HISTORYDB_API_URL = 'http://historydb-api-url/'
TEST_VALUE = 'test value'
TEST_IP = '1.1.1.1'
TEST_IP_2 = '2.2.2.2'
TEST_HINTQ_HINTA_TS_OFFSET = MAX_HINTQ_HINTA_TS_OFFSET * 0.9
TEST_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'
TEST_USER_AGENT_2 = 'libwww-perl/6.08'
TEST_YANDEXUID = '123'
TEST_DEFAULT_REGISTRATION_DATETIME = '2010-10-10 10:20:30'
TEST_DEFAULT_REGISTRATION_TIMESTAMP = int(datetime_to_unixtime(parse_datetime(TEST_DEFAULT_REGISTRATION_DATETIME)))


class TranslationSettings(object):
    QUESTIONS = {'en': {'11': 'Your favourite teacher'}}
