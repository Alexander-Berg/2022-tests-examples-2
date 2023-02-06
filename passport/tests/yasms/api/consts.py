# -*- coding: utf-8 -*-

from datetime import datetime

from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_ID1 = 25
TEST_PHONE_ID2 = 55
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79259164525')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79026411724')
TEST_EMAIL1 = 'hello@yandex.ru'
TEST_FIRSTNAME1 = u'Андрей'
TEST_LOGIN1 = 'test-login1'
TEST_OPERATION_ID1 = 17
TEST_OPERATION_ID2 = 19
TEST_CONFIRMATION_CODE1 = '1234'
TEST_CONSUMER1 = 'test-consumer1'
TEST_UID1 = 37
TEST_TIME1 = datetime(2014, 5, 10, 2, 1, 3)
TEST_USER_AGENT = 'curl'
TEST_IP = '1.2.3.4'
TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+22503123456', country='CI', allow_impossible=True)
TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+2250103123456', country='CI', allow_impossible=True)
