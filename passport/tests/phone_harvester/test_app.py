from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)
from functools import partial

from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_operations_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.models.phones.faker import (
    assert_simple_phone_bound,
    build_account,
    build_mark_operation,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.dbscripts.phone_harvester import cli as app
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_BLACKBOX_URL1,
    TEST_OPERATION_ID1,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER1,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.utils.common import deep_merge


@with_settings_hosts(
    BLACKBOX_URL=TEST_BLACKBOX_URL1,
)
class TestRun(TestCase):
    def test_no_phone_operations(self):
        self._blackbox_faker.set_response_value(
            'phone_operations',
            blackbox_phone_operations_response([]),
        )

        app.run(dynamic=True)

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})
        eq_(self._mailer_faker.messages, [])

    def test_has_phone_operations(self):
        self._blackbox_faker.set_response_value(
            'phone_operations',
            blackbox_phone_operations_response([
                {
                    'uid': TEST_UID1,
                    'phone_id': TEST_PHONE_ID1,
                    'id': TEST_OPERATION_ID1,
                    'type': 'mark',
                    'security_identity': TEST_PHONE_NUMBER1.digital,
                    'started': datetime.now() - timedelta(hours=2),
                    'finished': datetime.now() - timedelta(hours=1),
                },
            ]),
        )
        build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            uid=TEST_UID1,
            **deep_merge(
                build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_mark_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        app.run(dynamic=True)

        assert_simple_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='mark',
            ),
        ])

        phone_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': 'harvest_expired_phone_operations',
            phone_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op_fmt('type'): 'mark',
            op_fmt('security_identity'): TEST_PHONE_NUMBER1.digital,
            op_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_phone_operations_request(self):
        self._blackbox_faker.set_response_value(
            'phone_operations',
            blackbox_phone_operations_response([]),
        )

        app.run(dynamic=True)

        self._blackbox_faker.requests[0].assert_query_contains({
            'method': 'phone_operations',
            'finished_before': TimeNow(),
        })

    def test_non_unique_uids(self):
        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([{'uid': None}, {'uid': None}]),
        )

        app.run(uids=[TEST_UID1, TEST_UID2, TEST_UID1])

        request = self._blackbox_faker.requests[0]
        uids = ','.join(map(str, [TEST_UID1, TEST_UID2]))
        request.assert_post_data_contains({'uid': uids})
