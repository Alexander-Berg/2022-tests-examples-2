# -*- coding: utf-8 -*-

from datetime import datetime

from passport.backend.core.env import Environment
from passport.backend.core.test.consts import TEST_USER_IP1
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID1 = 13
TEST_UID2 = 17
TEST_UID3 = 19

TEST_PHONE_ID1 = 25
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79259164525')
TEST_CONSUMER1 = 'dev'
TEST_TIME1 = datetime(2000, 1, 1)
TEST_ENVIRONMENT1 = Environment(user_agent='curl', user_ip=TEST_USER_IP1)
TEST_BINDING_LIMIT = 2
TEST_DISPLAY_LANGUAGES = ('ru', 'en')
TEST_ALL_SUPPORTED_LANGUAGES = {
    'all': TEST_DISPLAY_LANGUAGES,
    'default': TEST_DISPLAY_LANGUAGES[0],
}


class TranslationSettings(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.NOTIFICATIONS = {lang: EchoDict() for lang in TEST_DISPLAY_LANGUAGES}


class EchoDict(object):
    def __getitem__(self, key):
        return key
