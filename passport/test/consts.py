# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.core.env import Environment
from passport.backend.core.test.consts import *  # noqa
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_ACTION1 = 'create_heavens_and_the_earth'

TEST_APPLICATION_ID1 = 4571

TEST_BLACKBOX_URL1 = 'http://black/box'

TEST_ENVIRONMENT1 = Environment()

TEST_LOGIN1 = 'plato'
TEST_FIRSTNAME1 = 'Платон'
TEST_LASTNAME1 = 'Афинский'
TEST_DISPLAY_NAME1 = {'name': TEST_LASTNAME1}
TEST_EMAIL1 = TEST_LOGIN1 + '@yandex.ru'
TEST_EMAIL_ID1 = 100
TEST_BIRTHDATE1 = '1990-01-02'
TEST_BIRTHDATE2 = '1995-12-17'

TEST_LOGIN2 = 'ershov'
TEST_FIRSTNAME2 = 'Андрей'
TEST_LASTNAME2 = 'Ершов'
TEST_EMAIL2 = TEST_LOGIN2 + '@yandex.ru'
TEST_EMAIL_ID2 = 500

TEST_OPERATION_ID1 = 1
TEST_OPERATION_ID2 = 2
TEST_OPERATION_ID3 = 3

TEST_PHONE_ID1 = 1
TEST_PHONE_ID2 = 3
TEST_PHONE_ID3 = 5

TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79123456789')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79234567891')
TEST_PHONE_NUMBER3 = PhoneNumber.parse('+79234567892')

TEST_SHORT_OPERATION_TTL = timedelta(minutes=7)

TEST_UID1 = 1
TEST_UID2 = 5
TEST_UID3 = 6

TEST_DEFAULT_AVATAR_KEY1 = 'avatar_key1'

TEST_COUNTRY_CODE1 = 'ua'
TEST_CITY1 = 'Киев'
TEST_TIMEZONE1 = 'Europe/Kiev'

TEST_DATETIME1 = datetime(2015, 2, 3, 1, 2, 3)
TEST_DATETIME2 = datetime(2015, 3, 7, 12, 59, 32)

TEST_BACKUP_1 = 'abc123456def'
TEST_BACKUP_2 = 'abc654321def'
TEST_BACKUP_3 = 'cba654321fed'
TEST_DATETIME_LONG_AGO = datetime(1971, 1, 1)

TEST_FAMILY_ID = 'f1'
