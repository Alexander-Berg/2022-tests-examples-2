# -*- coding: utf-8 -*-
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_PRIORITY = 5
TEST_REASON = 'reason'
TEST_YT_RESPONSE = [{'uid': TEST_UID, 'begin_unixtime': 1}]
TEST_YT_PARSED_RESPONSE = TEST_YT_RESPONSE[0]

TEST_PHONE_ID1 = 1
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
