# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_VOLUNTARY_PASSWORD_CHANGE
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_WRONG_GUARD_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base_test_data import (
    TEST_CLEANED_PDD_RETPATH,
    TEST_COOKIE,
    TEST_CYRILLIC_PDD_LOGIN,
    TEST_DOMAIN,
    TEST_HOST,
    TEST_IDNA_DOMAIN,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_ORIGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_PUNYCODE_DOMAIN,
    TEST_RETPATH,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)


class BaseChangePasswordSubmitTestCase(BaseBundleTestViews, EmailTestMixin):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['account.change_password'])

        account_kwargs = self.account_kwargs()
        phone_kwargs = build_phone_bound(
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        kwargs = deep_merge(account_kwargs, phone_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_DOMAIN),
        )

        self.default_url = '/1/bundle/change_password/submit/?consumer=dev'

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def build_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, user_ip=TEST_USER_IP):
        return mock_headers(
            user_ip=user_ip,
            user_agent=TEST_USER_AGENT,
            cookie=cookie,
            host=host,
        )

    def account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN, alias_type='portal',
                       cryptpasswd='1:secret', **kwargs):
        base_kwargs = dict(
            uid=uid,
            login=login,
            attributes={'password.encrypted': cryptpasswd},
            aliases={alias_type: login},
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        return merge_dicts(base_kwargs, kwargs)

    def get_expected_response(self, state=None,
                              validation_method=u'captcha', uid=TEST_UID,
                              is_pdd=False, retpath=TEST_RETPATH,
                              punycode_domain=TEST_DOMAIN, unicode_domain=TEST_DOMAIN,
                              login=TEST_LOGIN, number=TEST_PHONE_NUMBER, display_login=None,
                              success=True, revoke_all=True, allow_select_revokers=True):
        response = {
            'track_id': self.track_id,
            'retpath': retpath,
            'account': {
                'uid': uid,
                'login': login,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': login if display_login is None else display_login,
            },
        }
        if validation_method:
            response['validation_method'] = validation_method

        if is_pdd:
            response['account']['domain'] = {
                'unicode': unicode_domain,
                'punycode': punycode_domain,
            }
        if state:
            response.update(state=state)
        elif success:
            response.update(
                revokers={
                    'default': {
                        'tokens': revoke_all,
                        'web_sessions': revoke_all,
                        'app_passwords': revoke_all,
                    },
                    'allow_select': allow_select_revokers,
                },
            )
        return response

    def query_params(self, retpath=TEST_RETPATH, origin=None):
        return dict(
            retpath=retpath,
            origin=origin,
        )

    def create_blackbox_pdd_response(self, login=TEST_PDD_LOGIN):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    uid=TEST_PDD_UID,
                    login=login,
                    alias_type='pdd',
                )
            ),
        )

    def make_request(self, headers, data=None):
        return self.env.client.post(
            self.default_url,
            data=data or {},
            headers=headers,
        )

    def check_track(self, uid=TEST_UID, login=TEST_LOGIN,
                    is_password_change=True, retpath=TEST_RETPATH,
                    has_secure_phone_number=None, secure_phone_number=None,
                    is_captcha_required=True, can_use_secure_number_for_password_validation=False, origin=None):
        track = self.track_manager.read(self.track_id)
        eq_(track.process_name, PROCESS_VOLUNTARY_PASSWORD_CHANGE)
        eq_(track.uid, str(uid))
        eq_(track.login, login)
        eq_(track.country, 'ru')
        eq_(track.is_password_change, is_password_change)
        eq_(track.retpath, retpath)
        eq_(track.origin, origin)
        eq_(track.has_secure_phone_number, has_secure_phone_number)
        eq_(track.secure_phone_number, secure_phone_number)
        eq_(track.is_captcha_required, is_captcha_required)
        eq_(track.can_use_secure_number_for_password_validation, can_use_secure_number_for_password_validation)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='change_password_voluntarily',
            track_id=self.track_id,
            uid=TEST_UID,
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'defined_validation_method',
            _inherit_from='local_base',
            action='defined_validation_method',
            validation_method='captcha',
        )
        self.env.statbox.bind_entry(
            'loaded_secure_number',
            _inherit_from='local_base',
            action='loaded_secure_number',
            error='invalid_phone_number',
        )

    def check_statbox_records(self, uid=TEST_UID, validation_method='captcha',
                              loaded_secure_number=False, with_check_cookies=False, **kwargs):
        expected_entries = []
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies'))
        if loaded_secure_number:
            expected_entries.append(
                self.env.statbox.entry(
                    'loaded_secure_number',
                    uid=str(uid),
                    **kwargs
                ),
            )
        expected_entries.append(
            self.env.statbox.entry(
                'defined_validation_method',
                uid=str(uid),
                validation_method=validation_method,
                **kwargs
            ),
        )
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            expected_entries,
        )


@with_settings_hosts()
class ChangePasswordSubmitTestCase(BaseChangePasswordSubmitTestCase):

    def test_missing_client_ip(self):
        rv = self.make_request(
            headers=self.build_headers(
                user_ip=None,
            ),
        )

        self.assert_error_response(rv, ['ip.empty'])

    def test_missing_host(self):
        rv = self.make_request(
            headers=self.build_headers(
                host=None,
            ),
        )

        self.assert_error_response(rv, ['host.empty'])

    def test_missing_cookie(self):
        rv = self.make_request(headers=self.build_headers(cookie=None))

        self.assert_error_response(rv, ['cookie.empty'])

    def test_invalid_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        rv = self.make_request(
            headers=self.build_headers(cookie='Session_id='),
        )

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_invalid_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        rv = self.make_request(
            headers=self.build_headers(cookie='Session_id='),
        )

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(rv, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def test_2fa_account_invalid_type(self):
        """
        Проверяем, что попытка смены пароля у пользователя со включенным 2FA
        оборвется выдачей ошибки.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    attributes={
                        'account.2fa_on': '1',
                    },
                )
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(
            rv,
            ['account.2fa_enabled'],
            retpath=None,
            track_id=self.track_id,
        )

    def test_disabled_account_with_userinfo(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(rv, ['account.disabled'])

    def test_disabled_on_deletion_account_with_userinfo(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                }
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def test_normal_account_ok(self):
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())
        self.assert_ok_response(rv, **self.get_expected_response())
        self.check_track()
        self.check_statbox_records(with_check_cookies=True)

    def test_normal_account_with_origin_passed_ok(self):
        rv = self.make_request(
            data=self.query_params(origin=TEST_ORIGIN),
            headers=self.build_headers(),
        )
        self.assert_ok_response(rv, **self.get_expected_response())
        self.check_track(origin=TEST_ORIGIN)
        self.check_statbox_records(origin=TEST_ORIGIN, with_check_cookies=True)

    def test_normal_account_with_phone_ok(self):
        kwargs = self.account_kwargs()
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        kwargs = deep_merge(kwargs, phone_secured)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **kwargs
            ),
        )

        rv = self.make_request(headers=self.build_headers(), data=self.query_params())

        self.assert_ok_response(rv, **self.get_expected_response())
        self.check_track(
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            can_use_secure_number_for_password_validation=True,
        )
        self.check_statbox_records(with_check_cookies=True)

        self.env.blackbox.requests[0].assert_query_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def test_normal_account_with_strong_password_policy_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    subscribed_to=[67],
                    dbfields={
                        'subscription.login_rule.67': 1,
                    },
                    attributes={'password.encrypted': '1:secret'},
                )
            ),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())
        self.assert_ok_response(rv, **self.get_expected_response(allow_select_revokers=False))
        self.check_track()
        self.check_statbox_records(with_check_cookies=True)

    def test_normal_account_ok_empty_retpath(self):
        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=''))

        self.assert_ok_response(rv, **self.get_expected_response(retpath=None))
        self.check_track(retpath=None)
        self.check_statbox_records(with_check_cookies=True)

    def test_lite_account_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    uid=TEST_UID,
                    login=TEST_LITE_LOGIN,
                )
            ),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())

        self.assert_ok_response(rv, **self.get_expected_response(login=TEST_LITE_LOGIN))
        self.check_track(login=TEST_LITE_LOGIN)
        self.check_statbox_records(with_check_cookies=True)

    def test_pdd_account_ok(self):
        self.create_blackbox_pdd_response()

        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=TEST_PDD_RETPATH))

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                uid=TEST_PDD_UID,
                is_pdd=True,
                retpath=TEST_CLEANED_PDD_RETPATH,
                login=TEST_PDD_LOGIN,
            )
        )
        self.check_track(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, retpath=TEST_CLEANED_PDD_RETPATH)
        self.check_statbox_records(uid=TEST_PDD_UID, with_check_cookies=True)

    def test_pdd_account_ok_empty_retpath(self):
        self.create_blackbox_pdd_response()

        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=''))

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                uid=TEST_PDD_UID,
                is_pdd=True,
                retpath=None,
                login=TEST_PDD_LOGIN,
            )
        )
        self.check_track(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, retpath=None)
        self.check_statbox_records(uid=TEST_PDD_UID, with_check_cookies=True)

    def test_pdd_account_idna_encoded_retpath(self):
        """
        Удостоверимся, что все хорошо с idna доменом и
        что фиксим старый ретпас для пдд
        """
        self.create_blackbox_pdd_response(login=TEST_CYRILLIC_PDD_LOGIN)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1', domain=TEST_IDNA_DOMAIN),
        )

        retpath = u'%s/for/%s' % (TEST_RETPATH, TEST_IDNA_DOMAIN)
        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=retpath))

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                is_pdd=True,
                retpath=TEST_RETPATH,
                uid=TEST_PDD_UID,
                unicode_domain=TEST_IDNA_DOMAIN,
                punycode_domain=TEST_PUNYCODE_DOMAIN,
                login=TEST_CYRILLIC_PDD_LOGIN,
            )
        )
        self.check_statbox_records(uid=TEST_PDD_UID, with_check_cookies=True)

    def test_pdd_account_can_change_password_true(self):
        self.create_blackbox_pdd_response()

        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1', domain=TEST_DOMAIN),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=TEST_PDD_RETPATH))

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                uid=TEST_PDD_UID,
                is_pdd=True,
                retpath=TEST_CLEANED_PDD_RETPATH,
                login=TEST_PDD_LOGIN,
            )
        )
        self.check_track(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, retpath=TEST_CLEANED_PDD_RETPATH)
        self.check_statbox_records(uid=TEST_PDD_UID, with_check_cookies=True)

    def test_pdd_account_can_change_password_false(self):
        self.create_blackbox_pdd_response()

        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='0', domain=TEST_DOMAIN),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=TEST_PDD_RETPATH))

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                is_pdd=True,
                uid=TEST_PDD_UID,
                retpath=TEST_CLEANED_PDD_RETPATH,
                state='password_change_forbidden',
                validation_method=None,
                login=TEST_PDD_LOGIN,
            )
        )
        self.check_track(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            is_password_change=None,
            retpath=TEST_CLEANED_PDD_RETPATH,
            is_captcha_required=None,
            has_secure_phone_number=None,
            can_use_secure_number_for_password_validation=None,
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [self.env.statbox.entry('check_cookies')])

    def test_social_account_redirect(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={'social': TEST_SOCIAL_LOGIN},
                attributes={'password.encrypted': ''},
                emails=[
                    self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                state='complete_social',
                login=TEST_SOCIAL_LOGIN,
                validation_method=None,
                display_login='',
            )
        )
        self.check_track(
            login=TEST_SOCIAL_LOGIN,
            is_password_change=None,
            is_captcha_required=None,
            has_secure_phone_number=None,
            can_use_secure_number_for_password_validation=None,
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [self.env.statbox.entry('check_cookies')])

    def test_portal_account_with_social_alias(self):
        """У пользователя, подписанного на социальный SID, не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'portal': TEST_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
                subscribed_to=[58],
                attributes={'password.encrypted': ''},
                emails=[
                    self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                state='complete_social',
                login=TEST_LOGIN,
                validation_method=None,
            )
        )
        self.check_track(
            login=TEST_LOGIN,
            is_password_change=None,
            is_captcha_required=None,
            has_secure_phone_number=None,
            can_use_secure_number_for_password_validation=None,
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [self.env.statbox.entry('check_cookies')])

    def test_intranet_ok(self):
        with settings_context(IS_INTRANET=True):
            rv = self.make_request(headers=self.build_headers(), data=self.query_params())

        self.assert_ok_response(rv, **self.get_expected_response(revoke_all=False, allow_select_revokers=True))
        self.check_track()
        self.check_statbox_records(with_check_cookies=True)

    def test_account_without_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(cryptpasswd='')
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(
            rv,
            [u'account.without_password'],
            **self.get_expected_response(
                retpath=None,
                validation_method=None,
                success=False,
            )
        )
        self.check_track(
            is_password_change=None,
            retpath=None,
            is_captcha_required=None,
            has_secure_phone_number=None,
            can_use_secure_number_for_password_validation=None,
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [self.env.statbox.entry('check_cookies')])

    def test_blackbox_sessionid_wrong_guard_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )
        resp = self.make_request(headers=self.build_headers())
        self.assert_error_response(resp, error_codes=['sessguard.invalid'])
