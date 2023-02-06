import os

from kikimr.yndx.api.protos.persqueue_pb2 import WriteResponse
import mock
from passport.backend.core.logbroker.logbroker_base import (
    create_credentials,
    format_protobuf,
    format_protobuf_safe,
    TvmManagerCredentialsProvider,
)
from passport.backend.core.logbroker.test.constants import (
    TEST_CREDENTIALS_CONFIG_OAUTH,
    TEST_CREDENTIALS_CONFIG_TVM,
    TEST_OAUTH_TOKEN,
    TEST_TVM_ALIAS,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    smart_bytes,
    with_settings_hosts,
)
from passport.backend.core.tvm import TvmCredentialsManager
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID as TEST_TVM_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.core.ydb_client import YDB_AUTH_TICKET_HEADER


@with_settings_hosts
class TestTvmManagerCredentialsProvider(PassportTestCase):
    def setUp(self):
        self.tvm_credentials_manager = mock.Mock()

    def test_construct__no_credentials__error(self):
        with self.assertRaises(ValueError):
            TvmManagerCredentialsProvider(
                tvm_credentials_manager=self.tvm_credentials_manager,
            )

    def test_construct__excess_credentials__error(self):
        with self.assertRaises(ValueError):
            TvmManagerCredentialsProvider(
                tvm_credentials_manager=self.tvm_credentials_manager,
                tvm_alias=TEST_TVM_ALIAS,
                tvm_client_id=TEST_TVM_CLIENT_ID,
            )

    def test_auth_metadata__by_alias__ok(self):
        self.tvm_credentials_manager.get_ticket_by_alias.return_value = TEST_TICKET
        provider = TvmManagerCredentialsProvider(
            tvm_credentials_manager=self.tvm_credentials_manager,
            tvm_alias=TEST_TVM_ALIAS,
        )
        metadata = provider.auth_metadata()
        self.tvm_credentials_manager.get_ticket_by_alias.assert_called_once_with(TEST_TVM_ALIAS)
        self.assertEqual(metadata, [(YDB_AUTH_TICKET_HEADER, smart_bytes(TEST_TICKET))])

    def test_auth_metadata__by_client_id__ok(self):
        self.tvm_credentials_manager.get_ticket_by_client_id.return_value = TEST_TICKET
        provider = TvmManagerCredentialsProvider(
            tvm_credentials_manager=self.tvm_credentials_manager,
            tvm_client_id=TEST_TVM_CLIENT_ID,
        )
        metadata = provider.auth_metadata()
        self.tvm_credentials_manager.get_ticket_by_client_id.assert_called_once_with(TEST_TVM_CLIENT_ID)
        self.assertEqual(metadata, [(YDB_AUTH_TICKET_HEADER, smart_bytes(TEST_TICKET))])


@with_settings_hosts
class TestCreateCredentials(PassportTestCase):
    def setUp(self):
        self._fake_tvm_manager = FakeTvmCredentialsManager()
        self._fake_tvm_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': TEST_TVM_ALIAS,
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self._fake_oauth_provider = mock.Mock(name='oauth_provider')
        self._fake_oauth_provider_class = mock.Mock(
            name='OAuthTokenCredentialsProvider',
            return_value=self._fake_oauth_provider,
        )
        self._oauth_provider_patch = mock.patch(
            'passport.backend.core.logbroker.logbroker_base.OAuthTokenCredentialsProvider',
            self._fake_oauth_provider_class,
        )

        self._fake_tvm_manager.start()
        self._oauth_provider_patch.start()

    def tearDown(self):
        self._oauth_provider_patch.stop()
        self._fake_tvm_manager.stop()

    def test_tvm__ok(self):
        credentials = create_credentials(TEST_CREDENTIALS_CONFIG_TVM)
        self.assertIsInstance(credentials, TvmManagerCredentialsProvider)
        self.assertEqual(credentials._tvm_alias, TEST_TVM_ALIAS)
        self.assertIsNone(credentials._tvm_client_id)
        self.assertIsInstance(credentials.tvm_credentials_manager, TvmCredentialsManager)

    def test_oauth__ok(self):
        with mock.patch.dict('os.environ', {'LB_TOKEN': TEST_OAUTH_TOKEN}):
            credentials = create_credentials(TEST_CREDENTIALS_CONFIG_OAUTH)
        self.assertIs(credentials, self._fake_oauth_provider)
        self._fake_oauth_provider_class.assert_called_once_with(TEST_OAUTH_TOKEN)

    def test_oauth__no_env__error(self):
        with mock.patch.dict('os.environ'):
            if 'LB_TOKEN' in os.environ:
                del os.environ['LB_TOKEN']
            with self.assertRaisesRegexp(ValueError, r'"LB_TOKEN" is missing'):
                create_credentials(TEST_CREDENTIALS_CONFIG_OAUTH)

    def test_wrong_type__error(self):
        with self.assertRaisesRegexp(ValueError, r'Unsupported credentials type'):
            create_credentials({'credentials_type': 'wrong'})


class TestProtobufFormatter(PassportTestCase):
    def test_format__ok(self):
        self.assertEqual(
            format_protobuf(WriteResponse(init=WriteResponse.Init(partition=1))),
            "{'init': {'partition': 1}}",
        )

    def test_format__wrong_type__exception(self):
        with self.assertRaises(AttributeError):
            format_protobuf('abc')

    def test_safe_format__ok(self):
        self.assertEqual(
            format_protobuf_safe(WriteResponse(init=WriteResponse.Init(partition=1))),
            "{'init': {'partition': 1}}",
        )

    def test_safe_format__wrong_type__ok(self):
        self.assertRegexpMatches(format_protobuf_safe('abc\nabc'), r'abc\\nabc <!PB format error .+!>')
