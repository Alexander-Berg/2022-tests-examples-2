# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_HOST,
    TEST_OAUTH_TOKEN,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_COOKIE,
    TEST_USER_IP1,
    TEST_USER_TICKET1,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.crypto.signing import SigningRegistry
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.support_code import SupportCode
from passport.backend.core.serializers.ydb.public import to_ydb_rows
from passport.backend.core.serializers.ydb.support_code import (
    hash_support_code_value,
    SupportCodeSerializerConfiguration,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeSpan,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_user_ticket
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.processors.support_code import (
    FindSupportCodeYdbQuery,
    InsertSupportCodeYdbQuery,
)
import passport.backend.core.ydb_client as ydb
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_CODE1 = '123456'
TEST_SECRET_ID1 = '1'
TEST_SECRET_ID2 = '2'
TEST_SECRET_ID3 = '3'
TEST_SUPPORT_CODE_TTL1 = timedelta(seconds=300)


class BaseSupportCodeTestCase(BaseBundleTestViews):
    def setup_signing_registry(self):
        self.signing_registry = SigningRegistry()
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID2,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID1,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': 'secret1',
                    },
                    {
                        'id':   TEST_SECRET_ID2,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': 'secret2',
                    },
                ],
            },
        )
        LazyLoader.register('YandexAndYandexTeamSigningRegistry', lambda: self.signing_registry)

    def build_support_code(self, uid=TEST_UID1, expires_at=None):
        if expires_at is None:
            expires_at = datetime.now() + TEST_SUPPORT_CODE_TTL1
        return SupportCode(
            expires_at=expires_at,
            uid=uid,
            value=TEST_CODE1,
        )

    def build_support_code_serializer_configuration(self):
        return SupportCodeSerializerConfiguration(
            signing_registry=self.signing_registry,
            old_secret=self.signing_registry.get(TEST_SECRET_ID1),
            cur_secret=self.signing_registry.get(TEST_SECRET_ID2),
        )


@with_settings_hosts(
    BLACKBOX_URL='https://blackbox',
    SUPPORT_CODE_GENERATE_RETRIES=2,
    SUPPORT_CODE_LENGTH=6,
    SUPPORT_CODE_TTL=TEST_SUPPORT_CODE_TTL1.total_seconds(),
    SUPPORT_CODE_API_ENABLED=True,
)
class TestCreateSupportCode(BaseSupportCodeTestCase):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/support_code/create/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'cookie': TEST_USER_COOKIE,
        'host': TEST_HOST,
        'user_ip': TEST_USER_IP1,
    }

    def setUp(self):
        super(TestCreateSupportCode, self).setUp()
        self.env = ViewsTestEnvironment()
        fake_signing = mock.patch(
            'passport.backend.core.crypto.signing.urandom',
            return_value=b'',
        )

        self.__patches = [
            self.env,
            fake_signing,
        ]

        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        try:
            del self.signing_registry
        except AttributeError:
            pass
        del self.__patches
        del self.env
        super(TestCreateSupportCode, self).tearDown()

    def setup_environment(self):
        self.setup_grants()
        self.setup_blackbox()
        self.setup_signing_registry()
        self.setup_code_generator()
        self.setup_statbox_templates()

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'support_code': ['create'],
                    },
                ),
            },
        )

    def setup_blackbox(self):
        response = blackbox_sessionid_multi_response(uid=TEST_UID1)
        response = blackbox_sessionid_multi_append_user(response, uid=TEST_UID2)
        self.env.blackbox.set_response_side_effect('sessionid', [response])

        response = blackbox_oauth_response(uid=TEST_UID1, scope='passport:support_code')
        self.env.blackbox.set_response_side_effect('oauth', [response])

    def setup_code_generator(self):
        self.env.code_generator.set_response_side_effect([TEST_CODE1, TEST_CODE1])

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            action='create_support_code',
            ip=TEST_USER_IP1,
            mode='support_code',
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'create_support_code',
            _inherit_from=['base'],
            status='success',
            collisions='0',
        )
        self.env.statbox.bind_entry(
            'too_much_collisions',
            _inherit_from=['base'],
            status='too_much_collisions',
        )

    def assert_create_support_code_ok_response(self, rv):
        support_code = self.build_support_code()
        self.assert_ok_response(
            rv,
            expires_at=TimeSpan(datetime_to_integer_unixtime(support_code.expires_at)),
            support_code=support_code.value,
        )

    def assert_insert_support_code_query_executed(self, query, support_code=None):
        if not support_code:
            support_code = self.build_support_code()

        expires_at = datetime.fromtimestamp(query['parameters']['$expires_at1'])
        self.assertEqual(expires_at, DatetimeNow(timestamp=support_code.expires_at))

        support_code = SupportCode(
            expires_at=expires_at,
            uid=support_code.uid,
            value=support_code.value,
        )

        row1, row2 = to_ydb_rows(support_code, self.build_support_code_serializer_configuration())
        self.env.fake_ydb.assert_fake_query_equals(
            query,
            InsertSupportCodeYdbQuery(row1, row2),
            commit_tx=True,
        )

    def assert_blackbox_sessionid_request_ok(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_contains(
            {
                'method': 'sessionid',
                'userip': TEST_USER_IP1,
                'multisession': 'yes',
            },
        )

    def assert_blackbox_oauth_request_ok(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_contains(
            {
                'method': 'oauth',
                'userip': TEST_USER_IP1,
                'oauth_token': TEST_OAUTH_TOKEN,
            },
        )

    def test_session(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_create_support_code_ok_response(rv)

        self.assertEqual(len(self.env.fake_ydb.executed_queries()), 1)
        self.assert_insert_support_code_query_executed(self.env.fake_ydb.executed_queries()[0])

        self.assertEqual(len(self.env.blackbox.requests), 1)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', ['action', 'ip', 'uid']),
                self.env.statbox.entry('create_support_code'),
            ],
        )

    def test_multisession(self):
        self.setup_environment()

        rv = self.make_request(query_args={'uid': TEST_UID2})

        self.assert_create_support_code_ok_response(rv)

        self.assertEqual(len(self.env.fake_ydb.executed_queries()), 1)
        self.assert_insert_support_code_query_executed(
            self.env.fake_ydb.executed_queries()[0],
            self.build_support_code(uid=TEST_UID2),
        )

        self.assertEqual(len(self.env.blackbox.requests), 1)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', ['action', 'ip', 'uid']),
                self.env.statbox.entry(
                    'create_support_code',
                    uid=str(TEST_UID2),
                ),
            ],
        )

    def test_oauth_token(self):
        self.setup_environment()

        rv = self.make_request(
            headers={
                'authorization': 'Oauth ' + TEST_OAUTH_TOKEN,
            },
            exclude_headers=['cookie'],
        )

        self.assert_create_support_code_ok_response(rv)

        self.assertEqual(len(self.env.fake_ydb.executed_queries()), 1)
        self.assert_insert_support_code_query_executed(self.env.fake_ydb.executed_queries()[0])

        self.assertEqual(len(self.env.blackbox.requests), 1)
        self.assert_blackbox_oauth_request_ok(self.env.blackbox.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_support_code'),
            ],
        )

    def test_code_exists(self):
        self.setup_environment()
        self.env.fake_ydb.set_execute_side_effect(
            [
                ydb.PreconditionFailed(''),
                [FakeResultSet([])],
            ],
        )

        rv = self.make_request()

        self.assert_create_support_code_ok_response(rv)

        self.assertEqual(len(self.env.fake_ydb.executed_queries()), 2)
        self.assert_insert_support_code_query_executed(self.env.fake_ydb.executed_queries()[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', ['action', 'ip', 'uid']),
                self.env.statbox.entry(
                    'create_support_code',
                    collisions='1',
                ),
            ],
        )

    def test_code_exist_and_retries_not_help(self):
        self.setup_environment()
        self.env.fake_ydb.set_execute_side_effect(ydb.PreconditionFailed(''))

        rv = self.make_request()

        self.assert_error_response(rv, ['internal.temporary'])

        self.assertEqual(len(self.env.fake_ydb.executed_queries()), 2)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', ['action', 'ip', 'uid']),
                self.env.statbox.entry('too_much_collisions'),
            ],
        )

    def test_api_disabled(self):
        self.setup_environment()
        with settings_context(
            SUPPORT_CODE_API_ENABLED=False,
        ):
            rv = self.make_request()
        self.assert_error_response(rv, ['internal.permanent'])


@with_settings_hosts(
    SUPPORT_CODE_API_ENABLED=True,
)
class TestCheckSupportCode(BaseSupportCodeTestCase):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/support_code/check/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'host': TEST_HOST,
        'user_ip': TEST_USER_IP1,
        'user_ticket': TEST_USER_TICKET1,
    }
    http_query_args = {
        'support_code': TEST_CODE1,
    }

    def setUp(self):
        super(TestCheckSupportCode, self).setUp()
        self.env = ViewsTestEnvironment()

        self.__patches = [
            self.env,
        ]

        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.signing_registry
        del self.__patches
        del self.env
        super(TestCheckSupportCode, self).tearDown()

    def setup_environment(self):
        self.setup_grants()
        self.setup_signing_registry()
        self.setup_ydb()
        self.setup_statbox_templates()
        self.setup_ticket_checker()

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'support_code': ['check'],
                    },
                ),
            },
        )

    def setup_ydb(self):
        support_code = self.build_support_code()
        self.env.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    to_ydb_rows(
                        support_code,
                        self.build_support_code_serializer_configuration(),
                    ),
                )],
            ],
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'check_support_code',
            action='check_support_code',
            ip=TEST_USER_IP1,
            mode='support_code',
            status='success',
            support_uid=str(TEST_UID1),
            uid=str(TEST_UID1),
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
            uids=uids,
        )

    def assert_check_support_code_ok_response(self, rv, uid=TEST_UID1):
        self.assert_ok_response(rv, uid=uid)

    def assert_support_code_queried(
        self,
        code=TEST_CODE1,
        old_secret_id=TEST_SECRET_ID1,
        cur_secret_id=TEST_SECRET_ID2,
    ):
        hash1 = hash_support_code_value(code, self.signing_registry.get(old_secret_id))
        hash2 = hash_support_code_value(code, self.signing_registry.get(cur_secret_id))
        self.env.fake_ydb.assert_queries_executed(
            [
                FindSupportCodeYdbQuery(hash2, hash1),
            ],
        )

    def test_valid_secret(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_check_support_code_ok_response(rv)
        self.assert_support_code_queried()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_support_code'),
            ],
        )

    def test_invalid_support_code(self):
        self.setup_environment()

        rv = self.make_request(query_args={'support_code': u'тыц'})

        self.assert_check_support_code_ok_response(rv)
        self.assert_support_code_queried(u'тыц')
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_support_code'),
            ],
        )

    def test_invalid_secret(self):
        self.setup_environment()
        self.signing_registry.remove(TEST_SECRET_ID1)
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID3,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID3,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': 'secret3',
                    },
                ],
            },
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['support_code.invalid'])
        self.assert_support_code_queried(
            old_secret_id=TEST_SECRET_ID2,
            cur_secret_id=TEST_SECRET_ID3,
        )
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'check_support_code',
                    status='fail',
                    _exclude=['uid'],
                ),
            ],
        )

    def test_api_disabled(self):
        self.setup_environment()
        with settings_context(SUPPORT_CODE_API_ENABLED=False):
            rv = self.make_request()
        self.assert_error_response(rv, ['internal.permanent'])
