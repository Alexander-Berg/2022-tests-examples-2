# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_CAPTCHA_SCALE_FACTOR,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_TRACK_ID,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_EXTERNAL_EMAIL1,
    TEST_FEDERAL_LOGIN,
    TEST_LANGUAGE,
    TEST_LOGIN,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_NUMBER_DUMPED_MASKED,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
    TEST_YANDEX_TEST_LOGIN,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api import SocialApiTemporaryError
from passport.backend.core.builders.social_api.faker.social_api import (
    get_profiles_response,
    profile_item,
)
from passport.backend.core.builders.ufo_api.faker import (
    TEST_FRESH_ITEM,
    ufo_api_profile_item,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.consts import (
    TEST_CONFIRMATION_CODE1,
    TEST_TRACK_ID2,
    TEST_UNIXTIME1,
    TEST_UNIXTIME2,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge


TEST_EXTERNAL_EMAIL = '%s@gmail.com' % TEST_LOGIN

TEST_FRESH_ITEM_WITH_DEVICE_ID = dict(
    TEST_FRESH_ITEM,
    device_id=TEST_DEVICE_ID,
)
TEST_FRESH_ITEM_WITH_CLOUD_TOKEN = dict(
    TEST_FRESH_ITEM,
    cloud_token=TEST_CLOUD_TOKEN,
)


@with_settings_hosts(
    ALLOW_AUTH_BY_SMS_FOR_MOBILE=True,
    ALLOW_AUTH_BY_SMS_FOR_MOBILE_ONLY_FOR_TEST_LOGINS=False,
    ALLOW_LITE_REGISTRATION=True,
    ALLOW_MAGIC_LINK=True,
    ALLOW_MAGIC_LINK_FOR_LITE=True,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    ALLOW_REGISTRATION=True,
    AUTH_BY_SMS_FOR_MOBILE__ALLOW_SKIP_SIB_CHECKS_FOR_TEST_LOGINS=False,
    AUTH_BY_SMS__ALLOW_SKIP_SIB_CHECKS=False,
    MOBILE_LITE_DATA_STATUS_DEFAULT={
        'name': 'not_used',
        'password': 'not_used',
        'phone_number': 'not_used',
    },
    SOCIAL_API_RETRIES=2,
    UFO_API_URL='http://localhost/',
    YDB_PERCENTAGE=0,
)
class TestStartView(BaseBundleTestViews, ProfileTestMixin):
    default_url = '/2/bundle/mobile/start/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
        'user_agent': 'curl',
    }
    http_query_args = {
        'x_token_client_id': TEST_X_TOKEN_CLIENT_ID,
        'x_token_client_secret': TEST_X_TOKEN_CLIENT_SECRET,
        'display_language': 'ru',
        'device_id': TEST_DEVICE_ID,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_manager = self.env.track_manager.get_manager()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(TEST_TRACK_ID)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['base']},
            ),
        )
        self.setup_statbox_templates()
        self.setup_blackbox_userinfo_response()
        self.setup_blackbox_loginoccupation_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_profile_responses([
            ufo_api_profile_item(data=TEST_FRESH_ITEM_WITH_DEVICE_ID),
        ])
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([]),
        )

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.track_manager
        del self.track_id_generator
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            type='mobile_start',
            ip=TEST_USER_IP,
            user_agent='curl',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'opened',
            action='opened',
            track_id=TEST_TRACK_ID,
            user_entered_login=TEST_LOGIN,
            device_id=TEST_DEVICE_ID,
        )

    def build_account(
        self,
        uid=TEST_UID,
        login=TEST_LOGIN,
        primary_alias_type='portal',
        enabled=True,
        has_password=True,
        has_2fa=False,
        with_social_alias=False,
        with_native_email=False,
        with_external_email=False,
        with_phonenumber_alias=False,
        subscribed_to=None,
        attributes=None,
        phone_number=None,
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        aliases = {
            primary_alias_type: login,
        }
        if with_social_alias:
            aliases.update({
                'social': TEST_SOCIAL_LOGIN,
            })
        if with_phonenumber_alias:
            aliases['phonenumber'] = phone_number.digital

        attributes = attributes or {}
        if has_2fa:
            attributes['account.2fa_on'] = '1'

        emails = []
        if with_native_email:
            emails.append(
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
            )
        if with_external_email:
            emails.append(
                self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com', default=not with_native_email),
            )

        account_kwargs = dict(
            uid=uid,
            login=login,
            crypt_password=TEST_PASSWORD_HASH if has_password else None,
            aliases=aliases,
            attributes=attributes,
            emails=emails,
            enabled=enabled,
            subscribed_to=subscribed_to,
        )
        if with_phonenumber_alias:
            phone_secured = build_phone_secured(
                1,
                phone_number.e164,
            )
            account_kwargs = deep_merge(account_kwargs, phone_secured)

        return account_kwargs

    def setup_blackbox_userinfo_response(self, **kwargs):
        account_kwargs = self.build_account(**kwargs)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )

    def setup_blackbox_loginoccupation_response(self, status='occupied'):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_LOGIN: status,
                TEST_EXTERNAL_EMAIL1: status,
                TEST_FEDERAL_LOGIN: status,
            }),
        )

    def setup_blackbox_hosted_domains_response(self, found=False):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1 if found else 0),
        )

    def check_blackbox_calls(self, login=TEST_LOGIN, call_count=1):
        eq_(len(self.env.blackbox.requests), call_count)
        if call_count >= 1:
            self.env.blackbox.requests[0].assert_post_data_contains({
                'method': 'userinfo',
                'login': login,
                'find_by_phone_alias': 'force_on',
                'country': 'US',
                'emails': 'getall',
            })
        if call_count >= 2:
            self.env.blackbox.requests[1].assert_query_contains({
                'method': 'loginoccupation',
            })
        if call_count >= 3:
            self.env.blackbox.requests[2].assert_query_contains({
                'method': 'hosted_domains',
            })

    def assert_statbox_ok(self, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('opened', **kwargs),
        ])

    def test_auth_ok(self):
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )

        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.allowed_auth_methods, ['password'])
        eq_(track.x_token_client_id, TEST_X_TOKEN_CLIENT_ID)
        eq_(track.x_token_client_secret, TEST_X_TOKEN_CLIENT_SECRET)
        eq_(track.display_language, TEST_LANGUAGE)
        ok_(track.cloud_token is not None)
        eq_(track.language, TEST_LANGUAGE)
        ok_(track.client_id is None)
        ok_(track.client_secret is None)
        ok_(track.avatar_size is None)
        ok_(track.captcha_scale_factor is None)
        ok_(track.payment_auth_retpath is None)
        ok_(track.device_name is None)
        ok_(track.country is None)
        eq_(track.user_entered_login, TEST_LOGIN)

    def test_ok_with_extra_params_and_second_client(self):
        resp = self.make_request(query_args={
            'login': TEST_LOGIN,
            'am_version_name': 'test-am-version',
            'device_id': TEST_DEVICE_ID,
            'device_name': TEST_DEVICE_NAME,
            'avatar_size': TEST_AVATAR_SIZE,
            'captcha_scale_factor': TEST_CAPTCHA_SCALE_FACTOR,
            'payment_auth_retpath': 'deeplink://am',
            'cloud_token': TEST_CLOUD_TOKEN,
            'display_language': 'en',
            'client_id': TEST_CLIENT_ID,
            'client_secret': TEST_CLIENT_SECRET,
        })
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )

        self.check_blackbox_calls()
        self.assert_statbox_ok(
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            am_version_name='test-am-version',
        )

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.allowed_auth_methods, ['password'])
        eq_(track.avatar_size, TEST_AVATAR_SIZE)
        eq_(track.captcha_scale_factor, str(TEST_CAPTCHA_SCALE_FACTOR))
        eq_(track.payment_auth_retpath, 'deeplink://am')
        eq_(track.cloud_token, TEST_CLOUD_TOKEN)
        eq_(track.account_manager_version, 'test-am-version')
        eq_(track.device_id, TEST_DEVICE_ID)
        eq_(track.device_name, TEST_DEVICE_NAME)
        eq_(track.display_language, 'en')
        ok_(track.country is None)
        eq_(track.x_token_client_id, TEST_X_TOKEN_CLIENT_ID)
        eq_(track.x_token_client_secret, TEST_X_TOKEN_CLIENT_SECRET)
        eq_(track.client_id, TEST_CLIENT_ID)
        eq_(track.client_secret, TEST_CLIENT_SECRET)

    def test_2fa_ok(self):
        self.setup_blackbox_userinfo_response(has_password=False, has_2fa=True)
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['otp'],
            primary_alias_type=1,
        )

        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()

    def test_social_profiles_ok(self):
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([
                profile_item(uid=TEST_UID),
            ]),
        )

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password', 'social_fb'],
            primary_alias_type=1,
        )
        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()

    def test_social_api_failed_ok(self):
        self.env.social_api.set_response_side_effect('get_profiles', SocialApiTemporaryError)

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )
        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()
        eq_(len(self.env.social_api.requests), 2)

    def test_account_without_auth_methods(self):
        self.setup_blackbox_userinfo_response(primary_alias_type='social', has_password=False)
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            auth_methods=[],
            primary_alias_type=6,
        )

        eq_(len(self.env.blackbox.requests), 1)

    def test_account_not_found_by_login(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            track_id=TEST_TRACK_ID,
            login=TEST_LOGIN,
        )

        self.check_blackbox_calls(call_count=2)  # userinfo + loginoccupation

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        eq_(track.user_entered_login, TEST_LOGIN)

    def test_account_not_found_by_yandex_email(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        resp = self.make_request(query_args={'login': '%s@yandex.ru' % TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            track_id=TEST_TRACK_ID,
            login=TEST_LOGIN,
        )

        self.check_blackbox_calls(login='%s@yandex.ru' % TEST_LOGIN, call_count=2)  # userinfo + loginoccupation
        self.assert_statbox_ok(user_entered_login='%s@yandex.ru' % TEST_LOGIN)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        eq_(track.user_entered_login, TEST_LOGIN)

    def test_account_not_found_by_phonenumber_alias(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'login': TEST_PHONE_NUMBER.original})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal', 'neophonish'],
            track_id=TEST_TRACK_ID,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
            country='us',
        )

        self.check_blackbox_calls(login=TEST_PHONE_NUMBER.original, call_count=1)
        self.assert_statbox_ok(user_entered_login=TEST_PHONE_NUMBER.original)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        ok_(track.user_entered_login is None)

    def test_account_not_found_by_lite_email(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        resp = self.make_request(query_args={'login': TEST_EXTERNAL_EMAIL1})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='lite',
            allowed_account_types=['lite'],
            track_id=TEST_TRACK_ID,
            login=TEST_EXTERNAL_EMAIL1,
            lite_data_necessity={
                'name': 'not_used',
                'password': 'not_used',
                'phone_number': 'not_used',
            },
        )

        self.check_blackbox_calls(
            login=TEST_EXTERNAL_EMAIL1,
            call_count=3,  # userinfo + loginoccupation + hosted_domains
        )
        self.assert_statbox_ok(user_entered_login=TEST_EXTERNAL_EMAIL1)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        eq_(track.user_entered_login, TEST_EXTERNAL_EMAIL1)

    def test_account_not_found_by_pdd_email(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')
        self.setup_blackbox_hosted_domains_response(found=True)

        resp = self.make_request(query_args={'login': TEST_EXTERNAL_EMAIL1})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(
            login=TEST_EXTERNAL_EMAIL1,
            call_count=3,  # userinfo + loginoccupation + hosted_domains
        )

    def test_force_register(self):
        resp = self.make_request(query_args={'login': TEST_PHONE_NUMBER.original, 'force_register': 'yes'})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal', 'neophonish'],
            track_id=TEST_TRACK_ID,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
            country='us',
        )

        eq_(len(self.env.blackbox.requests), 0)

    def test_account_blocked(self):
        self.setup_blackbox_userinfo_response(enabled=False)

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.disabled'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(call_count=1)  # userinfo

    def test_login_not_available_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('stoplist')

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['login.notavailable'],
            track_id=TEST_TRACK_ID,
        )

        eq_(len(self.env.blackbox.requests), 2)  # userinfo + loginoccupation

    def test_login_invalid_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'login': '^_^'})
        self.assert_error_response(
            resp,
            ['login.prohibitedsymbols'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login='^_^', call_count=1)  # в loginoccupation не идём, ибо логин заведомо невалиден

    def test_blackbox_invalid_params_error(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )

        resp = self.make_request(query_args={'login': 'a\nb'})
        self.assert_error_response(
            resp,
            ['login.prohibitedsymbols'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login='a\nb', call_count=1)  # в loginoccupation не идём, ибо логин заведомо невалиден

    def test_claimed_phone_number_invalid_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'login': 'i-am-phone-number', 'is_phone_number': 'yes'})
        self.assert_error_response(
            resp,
            ['phone_number.invalid'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login='i-am-phone-number', call_count=1)  # в loginoccupation не идём, ибо это заведомо не логин

    def test_detected_phone_number_invalid_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'login': '+7 (985)'})
        self.assert_error_response(
            resp,
            ['phone_number.invalid'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login='+7 (985)', call_count=1)  # в loginoccupation не идём, ибо это заведомо не логин

    def test_unable_to_register(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        with settings_context(ALLOW_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(call_count=2)  # userinfo + loginoccupation

    def test_federal_unable_to_register(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        with settings_context(ALLOW_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_FEDERAL_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login=TEST_FEDERAL_LOGIN, call_count=3)

    def test_unable_to_register_lite(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        with settings_context(ALLOW_LITE_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_EXTERNAL_EMAIL1})
        self.assert_error_response(
            resp,
            ['login.prohibitedsymbols'],
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(call_count=1, login=TEST_EXTERNAL_EMAIL1)  # userinfo

    def test_unable_to_register_neophonish(self):
        self.setup_blackbox_userinfo_response(uid=None)

        with settings_context(ALLOW_NEOPHONISH_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_PHONE_NUMBER.original})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            track_id=TEST_TRACK_ID,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
            country='us',
        )

        self.check_blackbox_calls(login=TEST_PHONE_NUMBER.original, call_count=1)
        self.assert_statbox_ok(user_entered_login=TEST_PHONE_NUMBER.original)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        ok_(track.user_entered_login is None)

    def test_social_with_login_without_password(self):
        self.setup_blackbox_userinfo_response(
            has_password=False,
            with_social_alias=True,
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            auth_methods=[],
            primary_alias_type=6,
        )

        self.check_blackbox_calls(login=TEST_LOGIN)

    def test_neophonish(self):
        self.setup_blackbox_userinfo_response(
            has_password=False,
            primary_alias_type='neophonish',
            with_phonenumber_alias=True,
        )
        resp = self.make_request(query_args={'login': TEST_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['sms_code'],
            phone_number=TEST_PHONE_NUMBER_DUMPED,
            country='us',
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            primary_alias_type=5,
            is_neophonish=True,
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(login=TEST_PHONE_NUMBER.original)

    def test_neophonish_with_old_ivory_coast_phone(self):
        self.check_neophonish_with_ivory_coast_phone(
            account_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_neophonish_with_new_ivory_coast_phone(self):
        self.check_neophonish_with_ivory_coast_phone(
            account_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_neophonish_with_ivory_coast_phone(self, account_phone_number, user_entered_phone_number):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**self.build_account(uid=None)),
                blackbox_userinfo_response(
                    **self.build_account(
                        has_password=False,
                        phone_number=account_phone_number,
                        primary_alias_type='neophonish',
                        with_phonenumber_alias=True,
                    )
                ),
            ]
        )

        resp = self.make_request(query_args={'login': user_entered_phone_number.original})

        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['sms_code'],
            phone_number=user_entered_phone_number.as_dict(),
            country='us',
            secure_phone_number=account_phone_number.as_dict(only_masked=True),
            primary_alias_type=5,
            is_neophonish=True,
            track_id=TEST_TRACK_ID,
        )

        self.env.blackbox.requests[0].assert_post_data_contains(
            dict(
                method='userinfo',
                login=user_entered_phone_number.e164,
            ),
        )
        self.env.blackbox.requests[1].assert_post_data_contains(
            dict(
                method='userinfo',
                login=account_phone_number.e164,
            ),
        )

    def test_neophonish_with_new_national_ivory_coast_phone(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**self.build_account(uid=None)),
                blackbox_userinfo_response(
                    **self.build_account(
                        has_password=False,
                        phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
                        primary_alias_type='neophonish',
                        with_phonenumber_alias=True,
                    )
                ),
            ]
        )

        fake_region = mock.Mock()
        fake_region.country = dict(short_en_name='CI')
        with mock.patch('passport.backend.api.common.suggest.Region', return_value=fake_region):
            resp = self.make_request(query_args={'login': TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.national})

        national_phone_number = PhoneNumber.parse(
            TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.national,
            country='CI',
            allow_impossible=True,
        )
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['sms_code'],
            phone_number=national_phone_number.as_dict(),
            country='ci',
            secure_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.as_dict(only_masked=True),
            primary_alias_type=5,
            is_neophonish=True,
            track_id=TEST_TRACK_ID,
        )

    def test_portal_with_magic_link(self):
        self.setup_blackbox_userinfo_response(
            with_native_email=True,
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'magic_link'],
            magic_link_email='%s@yandex.ru' % TEST_LOGIN,
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'magic_link'])
        eq_(track.uid, str(TEST_UID))

        self.check_blackbox_calls(login=TEST_LOGIN)

    def test_lite_with_magic_link(self):
        self.setup_blackbox_userinfo_response(
            login=TEST_EXTERNAL_EMAIL,
            primary_alias_type='lite',
            with_external_email=True,
        )
        resp = self.make_request(query_args={'login': TEST_EXTERNAL_EMAIL})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'magic_link'],
            magic_link_email=TEST_EXTERNAL_EMAIL,
            primary_alias_type=5,
            track_id=TEST_TRACK_ID,
        )

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'magic_link'])
        eq_(track.uid, str(TEST_UID))

        self.check_blackbox_calls(login=TEST_EXTERNAL_EMAIL)

    def test_magic_link_disabled(self):
        self.setup_blackbox_userinfo_response(
            with_native_email=True,
        )

        with settings_context(ALLOW_MAGIC_LINK=False):
            resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )

    def test_with_sms_code_by_device_id(self):
        self.setup_blackbox_userinfo_response(
            with_phonenumber_alias=True,
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'sms_code'],
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'sms_code'])
        ok_(track.has_secure_phone_number)
        eq_(track.secure_phone_number, TEST_PHONE_NUMBER.e164)

    def test_with_sms_code_by_cloud_token(self):
        self.setup_blackbox_userinfo_response(
            with_phonenumber_alias=True,
        )
        self.setup_profile_responses([
            ufo_api_profile_item(data=TEST_FRESH_ITEM_WITH_CLOUD_TOKEN),
        ])
        resp = self.make_request(query_args={'login': TEST_LOGIN, 'cloud_token': TEST_CLOUD_TOKEN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'sms_code'],
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'sms_code'])
        ok_(track.has_secure_phone_number)
        eq_(track.secure_phone_number, TEST_PHONE_NUMBER.e164)

    def test_sms_code_with_ignored_sib_checks_for_mobile(self):
        self.setup_blackbox_userinfo_response(
            login=TEST_YANDEX_TEST_LOGIN,
            with_phonenumber_alias=True,
        )
        self.setup_profile_responses([])

        with settings_context(AUTH_BY_SMS_FOR_MOBILE__ALLOW_SKIP_SIB_CHECKS_FOR_TEST_LOGINS=True):
            resp = self.make_request(query_args={'login': TEST_YANDEX_TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'sms_code'],
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_not_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'sms_code'])

    def test_sms_code_with_ignored_sib_checks_globally(self):
        self.setup_blackbox_userinfo_response(
            login=TEST_YANDEX_TEST_LOGIN,
            with_phonenumber_alias=True,
        )
        self.setup_profile_responses([])

        with settings_context(AUTH_BY_SMS__ALLOW_SKIP_SIB_CHECKS=True):
            resp = self.make_request(query_args={'login': TEST_YANDEX_TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password', 'sms_code'],
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_not_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password', 'sms_code'])

    def test_sms_code_not_allowed_by_ydb(self):
        self.setup_blackbox_userinfo_response(
            with_phonenumber_alias=True,
        )
        self.setup_profile_responses([])
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password'])

    def test_sms_code_not_allowed_for_strong_password(self):
        self.setup_blackbox_userinfo_response(
            with_phonenumber_alias=True,
            subscribed_to=[67],
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_not_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password'])

    def test_sms_code_allowed_only_for_test_logins(self):
        self.setup_blackbox_userinfo_response(with_phonenumber_alias=True)

        with settings_context(ALLOW_AUTH_BY_SMS_FOR_MOBILE_ONLY_FOR_TEST_LOGINS=True):
            resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_not_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password'])

    def test_sms_code_disabled(self):
        self.setup_blackbox_userinfo_response(
            with_phonenumber_alias=True,
            attributes={'account.sms_code_login_forbidden': '1'},
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            track_id=TEST_TRACK_ID,
        )
        self.assert_ufo_api_not_called()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.allowed_auth_methods, ['password'])

    def test_67_sid_social_auth_disable(self):
        self.setup_blackbox_userinfo_response(subscribed_to=[67])
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )
        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()
        self.assertEqual(self.env.social_api.requests, [])

    def test_2fa_social_auth_disable(self):
        self.setup_blackbox_userinfo_response(has_2fa=True)
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['otp'],
            primary_alias_type=1,
        )
        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()
        self.assertEqual(self.env.social_api.requests, [])

    def test_old_track_id(self):
        self.track_manager.create(
            track_type='authorize',
            consumer='dev',
            track_id=TEST_TRACK_ID2
        )
        with self.track_transaction(TEST_TRACK_ID2) as old_track:
            old_track.phone_confirmation_code = TEST_CONFIRMATION_CODE1
            old_track.phone_confirmation_first_checked = TEST_UNIXTIME1
            old_track.phone_confirmation_first_send_at = TEST_UNIXTIME1
            old_track.phone_confirmation_is_confirmed = True
            old_track.phone_confirmation_last_checked = TEST_UNIXTIME2
            old_track.phone_confirmation_last_send_at = TEST_UNIXTIME2
            old_track.phone_confirmation_method = 'by_sms'
            old_track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            old_track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.e164

        resp = self.make_request(
            query_args=dict(
                login=TEST_LOGIN,
                old_track_id=TEST_TRACK_ID2,
            ),
        )

        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.allowed_auth_methods, ['password'])
        eq_(track.user_entered_login, TEST_LOGIN)

        eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE1)
        eq_(track.phone_confirmation_first_checked, str(TEST_UNIXTIME1))
        eq_(track.phone_confirmation_first_send_at, str(TEST_UNIXTIME1))
        eq_(track.phone_confirmation_is_confirmed, True)
        eq_(track.phone_confirmation_last_checked, str(TEST_UNIXTIME2))
        eq_(track.phone_confirmation_last_send_at, str(TEST_UNIXTIME2))
        eq_(track.phone_confirmation_method, 'by_sms')
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.e164)
