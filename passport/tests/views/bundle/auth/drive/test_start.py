# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_IP1,
    TEST_USER_TICKET1,
)
from passport.backend.core import Undefined
from passport.backend.core.crypto.signing import SigningRegistry
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.drive import DriveSession
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)
from passport.backend.core.ydb.faker.ydb_keyvalue import FakeYdbKeyValue
from passport.backend.core.ydb.processors.drive import (
    find_drive_session,
    save_drive_session,
)
import passport.backend.core.ydb_client as ydb


DRIVE_DEVICE_ID1 = '1' * 32
DRIVE_DEVICE_ID2 = '2' * 32
DRIVE_SANDBOX_DEVICE_ID = '3' * 32
DRIVE_SESSION_ID1 = 'drive_session_id1'
DRIVE_SESSION_ID2 = 'drive_session_id2'


class BaseTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/auth/forward_drive/start/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_ticket': TEST_USER_TICKET1,
    }
    http_query_args = {
        'drive_device_id': DRIVE_DEVICE_ID1,
        'drive_session_id': DRIVE_SESSION_ID1,
    }
    consumer = TEST_CONSUMER1

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forward_drive': ['start'],
                    },
                ),
            },
        )

    def setup_ticket_checker(self, ticket=None):
        if ticket is None:
            ticket = self.build_user_ticket()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])

    def build_user_ticket(self, default_uid=TEST_UID1, uids=None):
        if uids is None:
            uids = [TEST_UID1]
        return fake_user_ticket(
            default_uid=default_uid,
            scopes=['carsharing:all'],
            uids=uids,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='forward_auth_to_drive_device',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
        )
        self.env.statbox.bind_entry(
            'revoke_drive_device',
            action='revoke_drive_device',
            uid=str(TEST_UID1),
            device_id=DRIVE_SANDBOX_DEVICE_ID,
        )
        self.env.statbox.bind_entry(
            'create_drive_session',
            action='create_drive_session',
            drive_device_id=DRIVE_DEVICE_ID1,
            uid=str(TEST_UID1),
            delete_old_session='0',
        )

    def assert_drive_session_saved(self, expected_drive_session=None):
        if expected_drive_session is None:
            expected_drive_session = self.build_drive_session(sandbox_device_id=Undefined)
        drive_session = find_drive_session(expected_drive_session.drive_device_id)
        self.assertEqual(drive_session, expected_drive_session)

    def assert_drive_session_not_saved(self):
        drive_session = find_drive_session(DRIVE_DEVICE_ID1)
        self.assertIsNone(drive_session)

    def build_drive_session(
        self,
        drive_device_id=DRIVE_DEVICE_ID1,
        sandbox_device_id=DRIVE_SANDBOX_DEVICE_ID,
        drive_session_id=DRIVE_SESSION_ID1,
        uid=TEST_UID1,
    ):
        return DriveSession(
            drive_device_id=drive_device_id,
            sandbox_device_id=sandbox_device_id,
            drive_session_id=drive_session_id,
            uid=uid,
        )

    def setup_signing_registry(self):
        signing_registry_config = {
            'default_version_id': '1',
            'versions': [
                {
                    'id':   '1',
                    'algorithm': 'SHA256',
                    'salt_length': 32,
                    'secret': '0' * 32,
                },
            ],
        }
        signing_registry = SigningRegistry()
        signing_registry.add_from_dict(signing_registry_config)
        LazyLoader.register('SigningRegistry', lambda: signing_registry)


@with_settings_hosts(
    DRIVE_AUTH_FORWARDING_API_ENABLED=True,
    OAUTH_CONSUMER='oauth_consumer',
    OAUTH_RETRIES=1,
    OAUTH_URL='https://oauth',
    TICKET_PARSER2_BLACKBOX_ENV='production',
    YDB_DRIVE_DATABASE='drive_database',
    YDB_DRIVE_ENABLED=True,
    YDB_RETRIES=1,
)
class TestStartView(BaseTestCase):
    def setUp(self):
        super(TestStartView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.fake_ydb_key_value = FakeYdbKeyValue()

        self.__patches = [
            self.env,
            self.fake_ydb_key_value,
        ]
        for patch in self.__patches:
            patch.start()

        self.setup_signing_registry()
        self.setup_grants()
        self.setup_ticket_checker()
        self.setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.fake_ydb_key_value
        del self.env
        super(TestStartView, self).tearDown()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_drive_session_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_drive_session'),
            ],
        )
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_invalid_user_ticket(self):
        self.setup_ticket_checker(fake_invalid_user_ticket(uids=[100500]))

        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.invalid'])
        self.assert_drive_session_not_saved()
        self.env.statbox.assert_equals([])

    def test_other_session_exists(self):
        old_drive_session = DriveSession(
            drive_device_id=DRIVE_DEVICE_ID2,
            drive_session_id=DRIVE_SESSION_ID2,
            uid=TEST_UID2,
        )
        save_drive_session(old_drive_session)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_drive_session_saved()
        self.assert_drive_session_saved(old_drive_session)
        self.env.statbox.assert_equals([self.env.statbox.entry('create_drive_session')])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_update_session(self):
        save_drive_session(self.build_drive_session(uid=TEST_UID1))
        self.setup_ticket_checker(
            self.build_user_ticket(
                default_uid=TEST_UID2,
                uids=[TEST_UID2],
            ),
        )

        rv = self.make_request(
            query_args={
                'drive_session_id': DRIVE_SESSION_ID2,
            },
        )

        self.assert_ok_response(rv)
        self.assert_drive_session_saved(
            self.build_drive_session(
                sandbox_device_id=Undefined,
                drive_session_id=DRIVE_SESSION_ID2,
                uid=TEST_UID2,
            ),
        )
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'revoke_drive_device',
                    uid=str(TEST_UID1),
                    device_id=DRIVE_SANDBOX_DEVICE_ID,
                ),
                self.env.statbox.entry(
                    'create_drive_session',
                    delete_old_session='1',
                    uid=str(TEST_UID2),
                    old_uid=str(TEST_UID1),
                ),
            ],
        )

    def test_update_session_without_sandbox_device_id(self):
        save_drive_session(self.build_drive_session(uid=TEST_UID1, sandbox_device_id=Undefined))
        self.setup_ticket_checker(
            self.build_user_ticket(
                default_uid=TEST_UID2,
                uids=[TEST_UID2],
            ),
        )

        rv = self.make_request(
            query_args={
                'drive_session_id': DRIVE_SESSION_ID2,
            },
        )

        self.assert_ok_response(rv)
        self.assert_drive_session_saved(
            self.build_drive_session(
                sandbox_device_id=Undefined,
                drive_session_id=DRIVE_SESSION_ID2,
                uid=TEST_UID2,
            ),
        )
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'create_drive_session',
                    delete_old_session='1',
                    uid=str(TEST_UID2),
                    old_uid=str(TEST_UID1),
                ),
            ],
        )

    def test_same_session_exists(self):
        save_drive_session(self.build_drive_session(sandbox_device_id=Undefined))

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_drive_session_saved()
        self.env.statbox.assert_equals([])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_ydb_failed(self):
        self.fake_ydb_key_value.set_response_side_effect([ydb.Timeout('timeout')])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.ydb_failed'])
        self.env.statbox.assert_equals([])
        self.assertEqual(len(self.env.oauth.requests), 0)


@with_settings_hosts(
    DRIVE_AUTH_FORWARDING_API_ENABLED=False,
)
class TestStartViewApiDisabled(BaseTestCase):
    def setUp(self):
        super(TestStartViewApiDisabled, self).setUp()
        self.env = ViewsTestEnvironment()

        self.__patches = [
            self.env,
        ]
        for patch in self.__patches:
            patch.start()

        self.setup_grants()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.env
        super(TestStartViewApiDisabled, self).tearDown()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])
        self.assertEqual(self.env.fake_ydb.executed_queries(), list())
        self.env.statbox.assert_equals(list())
