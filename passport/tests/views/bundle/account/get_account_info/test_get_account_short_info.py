# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_CYRILLIC_DOMAIN,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_OAUTH_SCOPE,
    TEST_PASSWORD_HASH,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PUBLIC_ID,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_oauth_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.account.account import ACCOUNT_TYPE_LITE
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)


ACCOUNT_SHORT_INFO_READ_GRANT = 'account.short_info_read'

TEST_LOGIN = 'Test-Login'
TEST_NATIVE_DOMAIN = 'yandex.ua'
TEST_LOGIN_NORMALIZED = 'test-login'
TEST_AVATAR_KEY = 'avakey'
TEST_MAILISH_ID = 'ORSXg5BNNvqws3djoNUC22LE'
TEST_NEOPHONISH_ID = 'nphne-PJAicnaocOAPINSCOPANScp'

TEST_UNIXTIME = 946674001
TEST_DATETIME_STR = datetime_to_string(unixtime_to_datetime(TEST_UNIXTIME))

TEST_PUBLIC_NAME = 'Mr N.'


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    MAILISH_DOMAIN_TO_PROVIDER={
        'gmail.com': 'gg',
        'hotmail.com': 'ms',
    },
)
class TestGetAccountShortInfoView(BaseBundleTestViews, EmailTestMixin):

    default_url = '/1/bundle/account/short_info/'
    http_query_args = dict(
        consumer='dev',
        avatar_size='normal',
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        authorization=TEST_AUTH_HEADER,
    )
    mocked_grants = [ACCOUNT_SHORT_INFO_READ_GRANT]

    def setup_blackbox_response(self, scope=TEST_OAUTH_SCOPE, login=TEST_LOGIN_NORMALIZED, display_login=TEST_LOGIN,
                                domain=None, default_alias_type='portal', yandexoid_alias=None,
                                display_name=TEST_DISPLAY_NAME_DATA, public_name=TEST_PUBLIC_NAME,
                                default_avatar_key=TEST_AVATAR_KEY,
                                with_password=False, with_native_email=False, with_default_email=False,
                                native_domain=TEST_NATIVE_DOMAIN, with_plus=False, email=None,
                                other_aliases=None, firstname=None, lastname=None, birthday=None, gender=None,
                                public_id=TEST_PUBLIC_ID, is_child=False,
                                **kwargs):
        attributes = {}
        if with_password:
            attributes['password.encrypted'] = '1:%s' % TEST_PASSWORD_HASH

        if with_plus:
            attributes['account.have_plus'] = '1'

        if is_child:
            attributes['account.is_child'] = '1'

        emails = []
        email_login, email_domain = email.rsplit('@', 1) if email else (TEST_LOGIN_NORMALIZED, 'gmail.com')
        if with_native_email:
            emails.append(
                self.create_native_email(email_login, native_domain),
            )
        elif with_default_email:
            emails.append(
                self.create_validated_external_email(email_login, email_domain, default=True),
            )

        aliases = dict({
            default_alias_type: login,
        }, **other_aliases or {})
        if yandexoid_alias:
            aliases.update(yandexoid=yandexoid_alias)

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                login=login,
                display_login=display_login,
                display_name=display_name,
                public_name=public_name,
                default_avatar_key=default_avatar_key,
                aliases=aliases,
                attributes=attributes,
                emails=emails,
                firstname=firstname,
                lastname=lastname,
                birthdate=birthday,
                gender=gender,
                oauth_token_info={'issue_time': TEST_DATETIME_STR},
                public_id=public_id,
                **kwargs
            ),
        )
        if domain:
            self.env.blackbox.set_blackbox_response_value(
                'hosted_domains',
                blackbox_hosted_domains_response(domain=domain),
            )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_minimal_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN_NORMALIZED,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_full_ok(self):
        self.setup_blackbox_response(
            yandexoid_alias='robot-test',
            default_avatar_key='0/0-0',
            is_avatar_empty=True,
            with_password=True,
            with_native_email=True,
            subscribed_to=[78, 668],
            with_plus=True,
            firstname='Vasya',
            lastname='Poupkine',
            birthday='2001-10-02',
            gender='1',
            is_child=True,
        )
        resp = self.make_request(query_args={'avatar_size': 'islands-9000'})
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN_NORMALIZED,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % ('0/0-0', 'islands-9000'),
            is_avatar_empty=True,
            native_default_email='%s@yandex.ua' % TEST_LOGIN_NORMALIZED,
            has_password=True,
            is_child=True,
            is_beta_tester=True,
            yandexoid_login='robot-test',
            has_plus=True,
            has_music_subscription=True,
            firstname='Vasya',
            lastname='Poupkine',
            birthday='2001-10-02',
            gender='m',
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_full_ok_with_unicode(self):
        self.setup_blackbox_response(
            yandexoid_alias='robot-test',
            default_avatar_key='0/0-0',
            is_avatar_empty=True,
            with_password=True,
            with_native_email=True,
            subscribed_to=[78, 668],
            native_domain=u'админкапдд.рф'.encode('idna').decode('utf8'),
            with_plus=True,
        )
        resp = self.make_request(query_args={'avatar_size': 'islands-9000'})
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN_NORMALIZED,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % ('0/0-0', 'islands-9000'),
            is_avatar_empty=True,
            native_default_email=u'%s@админкапдд.рф' % TEST_LOGIN_NORMALIZED,
            has_password=True,
            is_beta_tester=True,
            yandexoid_login='robot-test',
            has_plus=True,
            has_music_subscription=True,
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_not_native_default_email(self):
        self.setup_blackbox_response(
            yandexoid_alias='robot-test',
            default_avatar_key='0/0-0',
            is_avatar_empty=True,
            with_password=True,
            with_native_email=False,
            with_default_email=True,
            subscribed_to=[668],
        )
        resp = self.make_request(query_args={'avatar_size': 'islands-9000'})
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN_NORMALIZED,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % ('0/0-0', 'islands-9000'),
            is_avatar_empty=True,
            has_password=True,
            is_beta_tester=True,
            yandexoid_login='robot-test',
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_social_ok(self):
        self.setup_blackbox_response(
            default_alias_type='social',
            login='uid-test',
            display_login=None,
            display_name=TEST_SOCIAL_DISPLAY_NAME,
            public_name=None,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=6,
            display_name='Some User',
            public_name='Some User',
            social_provider='fb',
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_pdd_ok(self):
        self.setup_blackbox_response(
            default_alias_type='pdd',
            login=TEST_PDD_CYRILLIC_LOGIN,
            display_login=TEST_PDD_CYRILLIC_LOGIN,
            domain=TEST_CYRILLIC_DOMAIN,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=7,
            display_login=TEST_PDD_CYRILLIC_LOGIN,
            normalized_display_login=TEST_PDD_CYRILLIC_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    @parameterized.expand([
        ('gg', 'user@gmail.com'),
        ('gg', 'UsEr@gMaIl.cOm'),
        ('ms', 'user@hotmail.com'),
        (None, 'user@non_existing_social_provider.com'),
    ])
    def test_mailish_ok(self, expected_provider, email):
        self.setup_blackbox_response(
            default_alias_type='mailish',
            login=TEST_MAILISH_ID,
            display_name={'name': email},
            public_name=email,
            with_default_email=True,
            email=email,
        )

        resp = self.make_request()
        expected_response = {
            'uid': TEST_UID,
            'primary_alias_type': 12,
            'display_name': email,
            'public_name': email,
            'display_login': email,
            'normalized_display_login': email.lower(),
            'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            'x_token_issued_at': TEST_UNIXTIME,
            'public_id': TEST_PUBLIC_ID,
        }
        if expected_provider:
            expected_response['social_provider'] = expected_provider
        self.assert_ok_response(resp, **expected_response)

    def test_avatar_size_empty_error(self):
        resp = self.make_request(exclude_args=['avatar_size'])
        self.assert_error_response(
            resp,
            ['avatar_size.empty'],
        )

    def test_token_invalid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['oauth_token.invalid'],
        )

    def test_login_unnormalization_for_ios(self):
        resp = self.make_request(
            headers={'user_agent': 'com.yandex.mobile.auth.sdk/4.211.238 (Apple iPhone8,1; iOS 11.2.5)'},
        )
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_PUBLIC_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_social_with_login_without_password(self):
        self.setup_blackbox_response(
            other_aliases={
                'social': TEST_SOCIAL_LOGIN,
            },
            login=TEST_LOGIN,
            display_name=TEST_SOCIAL_DISPLAY_NAME,
            public_name=None,
            with_password=False,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            uid=TEST_UID,
            primary_alias_type=6,
            display_name='Some User',
            public_name='Some User',
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN_NORMALIZED,
            social_provider='fb',
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

    def test_neophonish_ok(self):
        self.setup_blackbox_response(
            default_alias_type='neophonish',
            login=TEST_NEOPHONISH_ID,
            display_login='',
            display_name={'name': TEST_SOCIAL_DISPLAY_NAME['name']},
            public_name=TEST_PUBLIC_NAME,
        )

        resp = self.make_request()
        expected_response = {
            'uid': TEST_UID,
            'primary_alias_type': ACCOUNT_TYPE_LITE,
            'display_name': TEST_SOCIAL_DISPLAY_NAME['name'],
            'public_name': TEST_PUBLIC_NAME,
            'display_login': TEST_NEOPHONISH_ID.lower(),
            'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
            'x_token_issued_at': TEST_UNIXTIME,
            'public_id': TEST_PUBLIC_ID,
        }

        self.assert_ok_response(resp, **expected_response)
