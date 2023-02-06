# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    FakeBlackbox,
)
from passport.backend.core.conf import settings
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils import (
    check_url_contains_params,
    with_settings,
)
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_error_codes,
)
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.account.account import (
    ACCOUNT_TYPE_KIDDISH,
    ACCOUNT_TYPE_KOLONKISH,
    ACCOUNT_TYPE_LITE,
    ACCOUNT_TYPE_NEOPHONISH,
    ACCOUNT_TYPE_PDD,
    ACCOUNT_TYPE_PHONISH,
    ACCOUNT_TYPE_SCHOLAR,
    ACCOUNT_TYPE_SOCIAL,
    ACCOUNT_TYPE_YAMBOT,
)
from passport.backend.core.types.login.faker.login import FakeLoginGenerator
from passport.backend.core.validators import (
    Invalid,
    State,
)
from passport.backend.core.validators.login.availability import (
    Availability,
    PublicIdAvailability,
)


GRANTS_FOR_CREATE_TEST_YANDEX_LOGIN = {
    (settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX + 'yandex-team'): {
        'grants': {},
        'networks': ['77.88.12.113'],
    },
    (settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX + 'yndx'): {
        'grants': {},
        'networks': ['178.154.221.128/25'],
    },
}


@with_settings(BLACKBOX_URL='http://localhost/')
class TestAvailabilityValidator(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.blackbox = FakeBlackbox()
        self.grants = FakeGrants()

        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                'username_free': 'free',
                'username_occupied': 'occupied',
                'username_malformed': 'malformed',
                'username_stoplist': 'stoplist',
                'yandex-team_free': 'free',
                'yandex-team_occupied': 'occupied',
                'yandex-team_stoplist': 'stoplist',
                'yndx_free': 'free',
                'yndx_occupied': 'occupied',
                'yndx_stoplist': 'stoplist',
                'uid-free': 'free',
                'uid-occupied': 'occupied',
                'uid-stoplist': 'stoplist',
                'phne-free': 'free',
                'phne-occupied': 'occupied',
                'phne-stoplist': 'stoplist',
                'nphne-free': 'free',
                'user@mk.ru': 'free',
                'user-occupied@mk.ru': 'occupied',
                'free@pdd-domain.ru': 'free',
                'yambot-bot': 'free',
                'yambot-bot-occupied': 'occupied',
                'kolonkish-123': 'free',
                'kolonkish-123-occupied': 'occupied',
                'kid-free': 'free',
                'kid-occupied': 'occupied',
                u'тарасвободна': 'free',
                u'гульназанята': 'occupied',
            }),
        )
        self.grants.set_grants_return_value({})

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.blackbox,
            self.grants,

        ]
        for patch in self.patches:
            patch.start()

        self.state = State(mock_env(user_ip='127.0.0.1'))
        self.yandex_geobase_state = State(mock_env(user_ip='37.9.101.188'))
        self.yandex_team_grant_state = State(mock_env(user_ip='77.88.12.113'))
        self.yndx_grant_state = State(mock_env(user_ip='178.154.221.128'))

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self.fake_tvm_credentials_manager
        del self.blackbox
        del self.grants
        del self.state
        del self.yandex_geobase_state
        del self.yandex_team_grant_state
        del self.yndx_grant_state

    def test_available_login(self):
        Availability().to_python({'login': 'username_free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=username_free' in url, self.blackbox.request.call_args)

    def test_empty_value_dict(self):
        eq_(Availability().to_python({}, self.state), {})

    @raises(Invalid)
    def test_unavailable_login(self):
        Availability().to_python({'login': 'username_occupied'}, self.state)

    @raises(Invalid)
    def test_stoplist_login(self):
        Availability().to_python({'login': 'username_stoplist'}, self.state)

    def test_ignore_stoplist_login(self):
        Availability().to_python({'login': 'username_free', 'ignore_stoplist': True}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=username_free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    def test_is_pdd_login(self):
        Availability(login_type=ACCOUNT_TYPE_PDD).to_python({'login': 'username_free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=username_free' in url, self.blackbox.request.call_args)
        ok_('is_pdd=1' in url, self.blackbox.request.call_args)

    def test_is_pdd_login_with_domain_field(self):
        Availability(
            login_type=ACCOUNT_TYPE_PDD,
            domain_field='domain',
        ).to_python(
            {
                'login': 'free',
                'domain': 'pdd-domain.ru',
            },
            self.state,
        )
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=free%40pdd-domain.ru' in url, self.blackbox.request.call_args)
        ok_('is_pdd=1' in url, self.blackbox.request.call_args)

    @raises(Invalid)
    def test_malformed_login(self):
        Availability().to_python({'login': 'username_malformed'}, self.state)

    def test_custom_login_field(self):
        Availability(login_field='yastaff_login').to_python({'yastaff_login': 'username_free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=username_free' in url, self.blackbox.request.call_args)

    def test_unavailable_testlogin(self):
        self.grants.set_grants_return_value(GRANTS_FOR_CREATE_TEST_YANDEX_LOGIN)
        params = [
            ({'login': 'yandex-team_free'}, self.state),
            ({'login': 'yandex-team_occupied'}, self.state),
            ({'login': 'yandex-team_stoplist'}, self.state),
            ({'login': 'yndx_free'}, self.state),
            ({'login': 'yndx_occupied'}, self.state),
            ({'login': 'yndx_stoplist'}, self.state),
            ({'login': 'yandex-team_occupied'}, self.yandex_geobase_state),
            ({'login': 'yndx_occupied'}, self.yandex_geobase_state),
            ({'login': 'yandex-team_occupied'}, self.yandex_team_grant_state),
            ({'login': 'yndx_occupied'}, State(mock_env(user_ip='178.154.221.128'))),
        ]

        for args, state in params:
            check_error_codes(Availability(), args, {'login': ['notAvailable']}, state)

    def test_allow_testlogin(self):
        self.grants.set_grants_return_value(GRANTS_FOR_CREATE_TEST_YANDEX_LOGIN)

        params = [
            ({'login': 'yandex-team_free', 'ignore_stoplist': True}, self.state),
            ({'login': 'yandex-team_free'}, self.yandex_geobase_state),
            ({'login': 'yandex-team_free'}, self.yandex_team_grant_state),
            ({'login': 'yndx_free', 'ignore_stoplist': True}, self.state),
            ({'login': 'yndx_free'}, self.yandex_geobase_state),
            ({'login': 'yndx_free'}, self.yndx_grant_state),
        ]

        for args, state in params:
            check_equality(Availability(), (args, args), state)

    def test_wait_user_defined_login_with_generated_login(self):
        params = [
            ({'login': 'uid-free'}, self.state),
            ({'login': 'uid-occupied'}, self.state),
            ({'login': 'uid-stoplist'}, self.state),
            ({'login': 'uid-stoplist', 'ignore_stoplist': True}, self.state),
        ]

        params.extend([({'login': g()}, self.state) for g in FakeLoginGenerator.get_login_generators().values()])

        for args, state in params:
            check_error_codes(Availability(), args, {'login': ['notAvailable']}, state)

    def test_wait_social_with_not_social(self):
        self.grants.set_grants_return_value(GRANTS_FOR_CREATE_TEST_YANDEX_LOGIN)
        params = [
            ({'login': 'username_free'}, self.state),
            ({'login': 'username_occupied'}, self.state),
            ({'login': 'username_malformed'}, self.state),
            ({'login': 'username_stoplist', 'ignore_stoplist': True}, self.state),
            # yndx | yandex-team тоже не пропускаем
            ({'login': 'yandex-team_free'}, self.yandex_team_grant_state),
            ({'login': 'yndx_free'}, self.yndx_grant_state),
            ({'login': 'yndx_stoplist', 'ignore_stoplist': True}, self.yndx_grant_state),
        ]

        for args, state in params:
            check_error_codes(Availability(login_type=ACCOUNT_TYPE_SOCIAL), args, {'login': ['notAvailable']}, state)

    def test_available_social_login(self):
        Availability(login_type=ACCOUNT_TYPE_SOCIAL).to_python({'login': 'uid-free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=uid-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    @raises(Invalid)
    def test_unavailable_social_login(self):
        Availability(login_type=ACCOUNT_TYPE_SOCIAL).to_python({'login': 'uid-occupied'}, self.state)

    def test_available_yambot_login(self):
        Availability(login_type=ACCOUNT_TYPE_YAMBOT).to_python({'login': 'yambot-bot'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        check_url_contains_params(url, dict(logins='yambot-bot', ignore_stoplist='1'))

    @raises(Invalid)
    def test_unavailable_yambot_login(self):
        Availability(login_type=ACCOUNT_TYPE_YAMBOT).to_python({'login': 'yambot-bot-occupied'}, self.state)

    def test_wait_not_yambot_with_yambot(self):
        params = [
            ({'login': 'username_free'}, self.state),
            ({'login': 'uid-free'}, self.state),
            ({'login': 'phne-free'}, self.state),
            ({'login': 'kolonkish-free'}, self.state),
        ]

        for args, state in params:
            check_error_codes(Availability(login_type=ACCOUNT_TYPE_YAMBOT), args, {'login': ['notAvailable']}, state)

    def test_available_kolonkish_login(self):
        Availability(login_type=ACCOUNT_TYPE_KOLONKISH).to_python({'login': 'kolonkish-123'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        check_url_contains_params(url, dict(logins='kolonkish-123', ignore_stoplist='1'))

    @raises(Invalid)
    def test_unavailable_kolonkish_login(self):
        Availability(login_type=ACCOUNT_TYPE_KOLONKISH).to_python({'login': 'kolonkish-123-occupied'}, self.state)

    def test_wait_not_kolonkish_with_kolonkish(self):
        params = [
            ({'login': 'username_free'}, self.state),
            ({'login': 'uid-free'}, self.state),
            ({'login': 'phne-free'}, self.state),
            ({'login': 'yambot-free'}, self.state),
        ]

        for args, state in params:
            check_error_codes(Availability(login_type=ACCOUNT_TYPE_KOLONKISH), args, {'login': ['notAvailable']}, state)

    def test_available_lite_login(self):
        Availability(login_type=ACCOUNT_TYPE_LITE).to_python({'login': 'user@mk.ru'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        check_url_contains_params(url, dict(logins='user@mk.ru', ignore_stoplist='1'))

    @raises(Invalid)
    def test_unavailable_lite_login(self):
        Availability(login_type=ACCOUNT_TYPE_LITE).to_python({'login': 'user-occupied@mk.ru'}, self.state)

    def test_ignore_stoplist_social_login(self):
        Availability(login_type=ACCOUNT_TYPE_SOCIAL).to_python({'login': 'uid-free', 'ignore_stoplist': True}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=uid-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    def test_wait_not_phonish_with_phonish(self):
        params = [
            ({'login': 'phne-free'}, self.state),
            ({'login': 'phne-occupied'}, self.state),
            ({'login': 'phne-stoplist'}, self.state),
            ({'login': 'phne-stoplist', 'ignore_stoplist': True}, self.state),
        ]

        for args, state in params:
            check_error_codes(Availability(), args, {'login': ['notAvailable']}, state)

    def test_wait_phonish_with_not_phonish(self):
        self.grants.set_grants_return_value(GRANTS_FOR_CREATE_TEST_YANDEX_LOGIN)
        params = [
            ({'login': 'username_free'}, self.state),
            ({'login': 'username_occupied'}, self.state),
            ({'login': 'username_malformed'}, self.state),
            ({'login': 'username_stoplist', 'ignore_stoplist': True}, self.state),
            # yndx | yandex-team тоже не пропускаем
            ({'login': 'yandex-team_free'}, self.yandex_team_grant_state),
            ({'login': 'yndx_free'}, self.yndx_grant_state),
            ({'login': 'yndx_stoplist', 'ignore_stoplist': True}, self.yndx_grant_state),
        ]

        for args, state in params:
            check_error_codes(Availability(login_type=ACCOUNT_TYPE_PHONISH), args, {'login': ['notAvailable']}, state)

    def test_available_phonish_login(self):
        Availability(login_type=ACCOUNT_TYPE_PHONISH).to_python({'login': 'phne-free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=phne-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    def test_available_neophonish_login(self):
        Availability(login_type=ACCOUNT_TYPE_NEOPHONISH).to_python({'login': 'nphne-free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=nphne-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    @raises(Invalid)
    def test_unavailable_phonish_login(self):
        Availability(login_type=ACCOUNT_TYPE_PHONISH).to_python({'login': 'phne-occupied'}, self.state)

    def test_ignore_stoplist_phonish_login(self):
        Availability(login_type=ACCOUNT_TYPE_PHONISH).to_python({'login': 'phne-free', 'ignore_stoplist': True}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=phne-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    @raises(ValueError)
    def test_unknown_login_type(self):
        Availability(login_type=999).to_python({'login': 'uid-free', 'ignore_stoplist': True}, self.state)

    def test_public_id(self):
        PublicIdAvailability().to_python({'public_id': 'username_free'}, self.state)

    @raises(Invalid)
    def test_occupied_public_id(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {'username_occupied': 'occupied'},
                {'username_occupied': '1'},
            ),
        )
        PublicIdAvailability().to_python({'public_id': 'username_occupied'}, self.state)

    def test_occupied_by_self_public_id(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {'username_occupied': 'occupied'},
                {'username_occupied': '1'},
            ),
        )
        PublicIdAvailability(uid=1).to_python({'public_id': 'username_occupied'}, self.state)

    def test_available_kiddish_login(self):
        Availability(login_type=ACCOUNT_TYPE_KIDDISH).to_python({'login': 'kid-free'}, self.state)
        url = self.blackbox.request.call_args[0][1]
        ok_('logins=kid-free' in url, self.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.blackbox.request.call_args)

    @raises(Invalid)
    def test_unavailable_kiddish_login(self):
        Availability(login_type=ACCOUNT_TYPE_KIDDISH).to_python({'login': 'kid-occupied'}, self.state)

    def test_available_scholar_login(self):
        login = u'тарасвободна'
        Availability(login_type=ACCOUNT_TYPE_SCHOLAR).to_python({'login': login}, self.state)
        self.blackbox.requests[0].assert_query_contains(
            dict(
                ignore_stoplist='1',
                logins=login,
            ),
        )

    @raises(Invalid)
    def test_unavailable_scholar_login(self):
        Availability(login_type=ACCOUNT_TYPE_KIDDISH).to_python({'login': 'гульназанята'}, self.state)

    @raises(Invalid)
    def test_scholar_login_not_valid_as_portal_alias(self):
        Availability().to_python({'login': u'вовочка'}, self.state)
