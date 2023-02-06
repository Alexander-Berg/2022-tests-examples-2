# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_operations_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .test_blackbox import BaseBlackboxTestCase


_UID1 = 17
_CONFIRMATION_CODE1 = '1234'
_PHONE_ID1 = 19
_PHONE_OPERATION_ID1 = 13

_TIME1 = datetime(2000, 1, 1, 0, 0, 1)
_TIME2 = datetime(2000, 1, 1, 0, 0, 2)
_TIME3 = datetime(2000, 1, 1, 0, 0, 3)
_TIME4 = datetime(2000, 1, 1, 0, 0, 4)
_TIME5 = datetime(2000, 1, 1, 0, 0, 5)


@with_settings(
    BLACKBOX_URL='http://blac.kb.ox/',
)
class TestPhoneOperations(BaseBlackboxTestCase):
    def setUp(self):
        super(TestPhoneOperations, self).setUp()
        self._blackbox_faker = FakeBlackbox()
        self._blackbox_faker.start()
        self._blackbox = Blackbox()

        self._blackbox_faker.set_response_value(
            'phone_operations',
            blackbox_phone_operations_response([]),
        )

    def tearDown(self):
        self._blackbox_faker.stop()
        del self._blackbox_faker
        super(TestPhoneOperations, self).tearDown()

    def test_request(self):
        self._blackbox.phone_operations(finished_before=_TIME1)

        self._blackbox_faker.requests[0].assert_query_equals({
            'method': 'phone_operations',
            'format': 'json',
            'finished_before': str(to_unixtime(_TIME1)),
        })

    def test_no_operations(self):
        phone_operations = self._blackbox.phone_operations(finished_before=_TIME1)
        eq_(phone_operations, [])

    def test_operation_exists(self):
        self._blackbox_faker.set_response_value(
            'phone_operations',
            blackbox_phone_operations_response([{
                'id': _PHONE_OPERATION_ID1,
                'uid': _UID1,
                'phone_id': _PHONE_ID1,
                'security_identity': 1,
                'type': 'remove',
                'started': _TIME1,
                'finished': _TIME5,
                'code_value': _CONFIRMATION_CODE1,
                'code_checks_count': 7,
                'code_send_count': 3,
                'code_last_sent': _TIME2,
                'code_confirmed': _TIME3,
                'password_verified': _TIME4,
            }]),
        )

        phone_operations = self._blackbox.phone_operations(finished_before=_TIME1)

        eq_(
            phone_operations,
            [{
                'id': _PHONE_OPERATION_ID1,
                'uid': _UID1,
                'phone_id': _PHONE_ID1,
                'security_identity': 1,
                'type': 'remove',
                'started': to_unixtime(_TIME1),
                'finished': to_unixtime(_TIME5),
                'code_value': _CONFIRMATION_CODE1,
                'code_checks_count': 7,
                'code_send_count': 3,
                'code_last_sent': to_unixtime(_TIME2),
                'code_confirmed': to_unixtime(_TIME3),
                'password_verified': to_unixtime(_TIME4),
                'flags': 0,
                'phone_id2': None,
            }],
        )
