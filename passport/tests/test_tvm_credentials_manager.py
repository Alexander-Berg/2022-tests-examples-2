# -*- coding: utf-8 -*-

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.tvm import (
    get_tvm_credentials_manager,
    TvmCredentialsManager,
)
from passport.backend.core.tvm.exceptions import (
    LoadTvmCredentialsError,
    UnavailableUserContextError,
    UnknownDestinationError,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_ALIAS,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_CLIENT_SECRET,
    TEST_KEYS,
    TEST_TICKET,
    TEST_TICKET_DATA,
)
from ticket_parser2 import BlackboxEnv


class TvmCredentialsManagerTestCase(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())
        self.fake_tvm_credentials_manager.start()
        self.manager = get_tvm_credentials_manager()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_load(self):
        eq_(self.manager.keys, TEST_KEYS)
        eq_(self.manager.client_id, TEST_CLIENT_ID)
        eq_(self.manager.client_secret, TEST_CLIENT_SECRET)

    def test_get_ticket_ok(self):
        eq_(self.manager.get_ticket_by_client_id(int(TEST_CLIENT_ID_2)), TEST_TICKET)
        eq_(self.manager.get_ticket_by_client_id(str(TEST_CLIENT_ID_2)), TEST_TICKET)
        eq_(self.manager.get_ticket_by_alias(TEST_ALIAS), TEST_TICKET)

    def test_service_context(self):
        ok_(self.manager.service_context.check(TEST_TICKET))

    @raises(UnknownDestinationError)
    def test_ticket_not_found_by_client_id(self):
        self.manager.get_ticket_by_client_id(42)

    @raises(UnknownDestinationError)
    def test_ticket_not_found_by_alias(self):
        self.manager.get_ticket_by_alias('foo')


@with_settings_hosts(
    TICKET_PARSER2_BLACKBOX_ENV=None,
)
class TestUserContextBlackboxEnvUndefined(PassportTestCase):
    def setUp(self):
        super(TestUserContextBlackboxEnvUndefined, self).setUp()
        self.fake_manager = FakeTvmCredentialsManager()
        self.fake_manager.set_data(fake_tvm_credentials_data())
        self.fake_manager.start()

    def tearDown(self):
        self.fake_manager.stop()
        del self.fake_manager
        super(TestUserContextBlackboxEnvUndefined, self).tearDown()

    def test_dont_fail_when_build_manager(self):
        get_tvm_credentials_manager()

    def test_fail_when_get_user_context(self):
        manager = get_tvm_credentials_manager()
        with self.assertRaises(UnavailableUserContextError):
            manager.get_user_context()


@with_settings_hosts(
    TICKET_PARSER2_BLACKBOX_ENV='production',
)
class TestUserContext(PassportTestCase):
    def setUp(self):
        super(TestUserContext, self).setUp()
        self.fake_manager = FakeTvmCredentialsManager()
        self.fake_manager.set_data(fake_tvm_credentials_data())
        self.fake_user_context_class = mock.Mock(name='FakeUserContext')

        self.__patches = [
            self.fake_manager,
            mock.patch(
                'passport.backend.core.tvm.tvm_credentials_manager.UserContext',
                self.fake_user_context_class,
            ),
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_manager
        del self.fake_user_context_class
        super(TestUserContext, self).tearDown()

    def build_manager(self, ticket_parser2_blackbox_env=None):
        manager = TvmCredentialsManager(
            ticket_parser2_blackbox_env=ticket_parser2_blackbox_env,
        )
        manager.load()
        return manager

    def test_internet_production(self):
        self.build_manager()
        self.fake_user_context_class.assert_called_once_with(BlackboxEnv.Prod, TEST_KEYS)

    def test_intranet_production(self):
        self.build_manager('intranet_production')
        self.fake_user_context_class.assert_called_once_with(BlackboxEnv.ProdYateam, TEST_KEYS)

    def test_get_user_context(self):
        user_context1 = object()
        self.fake_user_context_class.return_value = user_context1

        manager = self.build_manager()
        user_context2 = manager.get_user_context()

        self.assertIs(user_context1, user_context2)


class ReadTvmCredentialsTestCase(PassportTestCase):
    def setUp(self):
        self.load_json = mock.Mock(return_value='foo')
        self.load_json_patch = mock.patch(
            'passport.backend.core.tvm.tvm_credentials_manager.load_json',
            self.load_json,
        )
        self.load_json_patch.start()

        self.load_plaintext = mock.Mock(return_value='bar')
        self.load_plaintext_patch = mock.patch(
            'passport.backend.core.tvm.tvm_credentials_manager.load_plaintext',
            self.load_plaintext,
        )
        self.load_plaintext_patch.start()
        LazyLoader.flush('TvmCredentialsManager')

    def tearDown(self):
        self.load_plaintext_patch.stop()
        self.load_json_patch.stop()
        del self.load_plaintext
        del self.load_plaintext_patch
        del self.load_json
        del self.load_json_patch

    def test_first_load_with_value_error(self):
        self.load_json.side_effect = ValueError()
        with assert_raises(LoadTvmCredentialsError):
            get_tvm_credentials_manager()

    def test_first_load_with_io_error(self):
        self.load_plaintext.side_effect = IOError(2, u'No such file or directory')
        with assert_raises(LoadTvmCredentialsError):
            get_tvm_credentials_manager()

    def test_ok(self):
        self.load_plaintext.return_value = TEST_KEYS
        self.load_json.return_value = {
            'client_id': TEST_CLIENT_ID,
            'client_secret': TEST_CLIENT_SECRET,
            'tickets': TEST_TICKET_DATA,
        }
        with mock.patch('os.path.getmtime') as getmtime:
            getmtime.side_effect = [
                1,
                2,
            ]
            manager = get_tvm_credentials_manager()

        eq_(
            manager.config,
            {
                'keys': TEST_KEYS,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'tickets': TEST_TICKET_DATA,
            },
        )
        eq_(
            manager._files_mtimes,
            {
                '/var/cache/yandex/passport-tvm-keyring/tvm.keys': 1,
                '/var/cache/yandex/passport-tvm-keyring/passport.tickets': 2,
            },
        )
        eq_(
            self.load_plaintext.call_args_list,
            [
                (('/var/cache/yandex/passport-tvm-keyring/tvm.keys',),),
            ],
        )
        eq_(
            self.load_json.call_args_list,
            [
                (('/var/cache/yandex/passport-tvm-keyring/passport.tickets',),),
            ],
        )

    def test_without_secret_ok(self):
        self.load_plaintext.return_value = TEST_KEYS
        self.load_json.return_value = {
            'client_id': TEST_CLIENT_ID,
        }
        with mock.patch('os.path.getmtime') as getmtime:
            getmtime.side_effect = [
                1,
                2,
            ]
            manager = get_tvm_credentials_manager()

        eq_(
            manager.config,
            {
                'keys': TEST_KEYS,
                'client_id': TEST_CLIENT_ID,

            },
        )
        ok_(manager.client_secret is None)
