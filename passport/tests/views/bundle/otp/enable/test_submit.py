# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.social_api import BaseSocialApiError
from passport.backend.core.builders.social_api.faker.social_api import get_profiles_response
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_headers,
    TEST_IP,
    TEST_LOGIN,
    TEST_ORIGIN,
    TEST_PDD_DOMAIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_UID,
)


eq_ = iterdiff(eq_)


@with_settings_hosts
class SubmitV2TestCase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.default_headers = get_headers()

        _, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.track_manager, self.external_track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_side_effect([
            self.track_id,
            self.external_track_id,
        ])

        self.setup_blackbox()
        self.setup_social_api()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def get_account_kwargs(self, uid, login, alias_type='portal',
                           with_secure_phone=False, is_deleting=False,
                           has_password=True):
        account_kwargs = dict(
            uid=uid,
            login=login,
            aliases={
                alias_type: login,
            },
        )
        if has_password:
            account_kwargs['crypt_password'] = '1:crypt'

        if not is_deleting:
            phone_builder = build_phone_secured if with_secure_phone else build_phone_bound
            phone = phone_builder(
                1,
                TEST_PHONE_NUMBER.e164,
            )
            account_kwargs = deep_merge(account_kwargs, phone)
        else:
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )

            remove_operation = build_remove_operation(
                operation_id=1000,
                phone_id=1,
            )

            account_kwargs = deep_merge(
                phone_secured,
                remove_operation,
                account_kwargs,
            )

        return account_kwargs

    def setup_blackbox(self, account_kwargs=None):
        if account_kwargs is None:
            account_kwargs = self.get_account_kwargs(TEST_UID, TEST_LOGIN)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )

    def setup_social_api(self, response=None):
        response = response or {'profiles': []}
        self.env.social_api.set_social_api_response_value(response)

    def make_request(self, headers=None, **kwargs):
        if not headers:
            headers = self.default_headers
        return self.env.client.post(
            '/2/bundle/otp/enable/submit/?consumer=dev',
            data=kwargs,
            headers=headers,
        )

    def assert_track_ok(self, secure_number=None, retpath=None, uid=TEST_UID,
                        track_id=None, origin=None):
        track = self.track_manager.read(track_id or self.track_id)
        eq_(track.uid, str(uid))
        ok_(track.is_it_otp_enable)
        eq_(track.secure_phone_number, secure_number if secure_number is not None else '')
        eq_(track.has_secure_phone_number, secure_number is not None)
        eq_(track.retpath, retpath)
        eq_(track.origin, origin)

    def assert_blackbox_sessionid_called(self):
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

        self.env.blackbox.requests[0].assert_query_contains({
            'full_info': 'yes',
            'multisession': 'yes',
            'method': 'sessionid',
            'sessionid': '0:old-session',
            'sslsessionid': '0:old-sslsession',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='enable_otp',
            action='submitted',
            ip=TEST_IP,
            yandexuid='testyandexuid',
            user_agent='curl',
            uid=str(TEST_UID),
            consumer='dev',
            track_id=self.track_id,
        )
        for action in (
            'submitted',
            'skip_phone_confirmation',
        ):
            self.env.statbox.bind_entry(
                action,
                action=action,
            )

    def assert_state_response(self, resp, state):
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'ok',
                'state': state,
            }
        )

    def assert_ok_response(self, resp,
                           domain=None, uid=TEST_UID, login=TEST_LOGIN,
                           display_login=TEST_LOGIN, **kwargs):
        base_response = {
            'status': 'ok',
            'secure_number': None,
            'track_id': self.track_id,
            'skip_phone_check': False,
            'account': {
                'person': {
                    'firstname': u'\\u0414',
                    'language': u'ru',
                    'gender': 1,
                    'birthday': u'1963-05-15',
                    'lastname': u'\\u0424',
                    'country': u'ru'
                },
                'display_name': {u'default_avatar': u'', u'name': u''},
                'login': login,
                'uid': int(uid),
                'display_login': display_login,
            },
            'profiles': [],
        }
        if domain:
            base_response['account']['domain'] = domain
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs)
        )

    def test_empty_cookies_error(self):
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response(resp, ['sessionid.invalid'])

    def test_bad_cookies_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['sessionid.invalid'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                }
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_account_otp_already_enabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                attributes={'account.2fa_on': '1'},
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])

    def test_sms_2fa_enabled_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                have_password=True,
                uid=TEST_UID,
                attributes={
                    'account.sms_2fa_on': '1',
                    'account.forbid_disabling_sms_2fa': '1',
                },
                crypt_password='1:crypt',
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok(secure_number=None)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_account_no_password_error(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            has_password=False,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_error_response(resp, ['account.without_password'])

    def test_account_pdd_cant_change_password_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_PDD_DOMAIN, can_users_change_password='0'),
        )
        account_kwargs = self.get_account_kwargs(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            alias_type='pdd',
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_state_response(resp, 'password_change_forbidden')

    def test_social_account_need_complete(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login='uid-aasjf375',
            alias_type='social',
            has_password=False,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_state_response(resp, 'complete_social')

    def test_ok_no_secure_phone(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            with_secure_phone=False,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok(secure_number=None)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_with_secure_phone(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            with_secure_phone=True,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            secure_number=dict(
                TEST_PHONE_NUMBER_DUMPED,
                is_deleting=False,
            ),
        )
        self.assert_track_ok(secure_number=TEST_PHONE_NUMBER.e164)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_with_retpath(self):
        """
        Протестируем, что переданный ретпас сохраняем в трек
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_PDD_DOMAIN, can_users_change_password='1'),
        )
        account_kwargs = self.get_account_kwargs(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            alias_type='pdd',
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request(retpath='http://yandex.ru')
        self.assert_ok_response(
            resp,
            domain={'punycode': 'okna.ru', 'unicode': 'okna.ru'},
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            display_login=TEST_PDD_LOGIN,
        )
        self.assert_track_ok(
            secure_number=None,
            uid=str(TEST_PDD_UID),
            retpath='http://yandex.ru',
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                uid=str(TEST_PDD_UID),
            ),
        ])

    def test_ok_with_retpath_fix_for_pdd(self):
        """
        Убираем "/for/..." из retpath ПДДшника
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_PDD_DOMAIN, can_users_change_password='1'),
        )
        account_kwargs = self.get_account_kwargs(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            alias_type='pdd',
            with_secure_phone=False
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request(retpath='http://mail.yandex.ru/for/okna.ru')
        self.assert_ok_response(
            resp,
            domain={'punycode': 'okna.ru', 'unicode': 'okna.ru'},
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            display_login=TEST_PDD_LOGIN,
        )
        self.assert_track_ok(
            secure_number=None,
            uid=str(TEST_PDD_UID),
            retpath='http://mail.yandex.ru',
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                uid=str(TEST_PDD_UID),
            ),
        ])

    def test_ok_with_origin(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            with_secure_phone=False,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request(origin=TEST_ORIGIN)
        self.assert_ok_response(resp)
        self.assert_track_ok(secure_number=None, origin=TEST_ORIGIN)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                origin=TEST_ORIGIN,
            ),
        ])

    def test_ok_with_social_profiles__profiles_to_response(self):
        """
        Если у пользователя есть привязанные соц-профили, покажем их для предупреждения пользователя
        """
        # У пользователя есть соц-профили
        profiles = get_profiles_response()
        self.setup_social_api(
            profiles
        )

        resp = self.make_request()

        expected_profiles =[item for item in profiles['profiles'] if item['allow_auth']]
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            display_login=TEST_LOGIN,
            profiles=expected_profiles,
        )
        self.assert_track_ok(
            secure_number=None,
            uid=str(TEST_UID),
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_with_social_api_error(self):
        """
        Если социальное апи упало, то не обламываем весь процесс
        """
        # У пользователя есть соц-профили
        self.env.social_api.set_social_api_response_side_effect(BaseSocialApiError())

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            display_login=TEST_LOGIN,
        )
        self.assert_track_ok(
            secure_number=None,
            uid=str(TEST_UID),
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_with_secure_phone_is_deleting(self):
        """
        Начинаем включение 2fa. У пользователя есть защищенный телефон.
        Защищенный телефон в процессе удаления, сообщаем об этом.
        """
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            is_deleting=True,
        )
        self.setup_blackbox(account_kwargs)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            secure_number=dict(
                TEST_PHONE_NUMBER_DUMPED,
                is_deleting=True,
            ),
        )
        self.assert_track_ok(secure_number=TEST_PHONE_NUMBER.e164)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_external_track_passed(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            with_secure_phone=True,
        )
        self.setup_blackbox(account_kwargs)

        with self.track_manager.transaction(self.external_track_id).rollback_on_error() as track:
            track.is_otp_restore_passed = True
        resp = self.make_request(track_id=self.external_track_id)

        self.assert_track_ok(
            track_id=self.external_track_id,
            secure_number=TEST_PHONE_NUMBER.e164,
        )

        track = self.track_manager.read(self.external_track_id)
        eq_(track.track_id, self.external_track_id)
        ok_(track.is_otp_restore_passed)
        self.assert_ok_response(
            resp,
            skip_phone_check=True,
            track_id=self.external_track_id,
            secure_number=dict(
                TEST_PHONE_NUMBER_DUMPED,
                is_deleting=False,
            ),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'skip_phone_confirmation',
                track_id=self.external_track_id,
            ),
            self.env.statbox.entry(
                'submitted',
                track_id=self.external_track_id,
            ),
        ])
