# -*- coding: utf-8 -*-

from datetime import datetime

from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_loginoccupation_response,
    blackbox_lrandoms_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_successful_response,
    token_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    APP_PARTY_3RD_PARTY,
    APP_PARTY_YANDEX,
    get_bind_response,
    get_profiles_response,
    PROFILE_EMAIL,
    task_data_response,
)
from passport.backend.core.mailer.faker.mail_utils import EmailDatabaseMatcher
from passport.backend.core.models.email import Email
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_APPLICATION_ID1,
    TEST_CONSUMER1,
    TEST_DEFAULT_AVATAR1,
    TEST_DISPLAY_LOGIN1,
    TEST_EMAIL1,
    TEST_LOGIN1,
    TEST_MAILISH_LOGIN1,
    TEST_PASSWORD_HASH1,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER1,
    TEST_PHONISH_LOGIN1,
    TEST_RETPATH1,
    TEST_SOCIAL_LOGIN1,
    TEST_SOCIAL_TASK_ID1,
    TEST_TRACK_ID1,
    TEST_UID1,
    TEST_USER_IP1,
    TEST_YANDEX_EMAIL1,
    TEST_YANDEX_TOKEN1,
    TEST_YANDEXUID1,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
    remove_none_values,
)

from .base_test_data import TEST_AVATAR_URL
from .statbox_mixin import setup_statbox_templates


TEST_PROVIDER_TOKEN1 = 'token1'
TEST_YANDEX_CLIENT_ID1 = 'yci1'
TEST_YANDEX_CLIENT_SECRET1 = 'ycs1'


class TestBuilder(object):
    __test__ = False

    def __init__(self, env, social_login_generator):
        self._env = env
        self._fake_social_login_generator = social_login_generator

    def request_native_start(self, headers=None):
        raise NotImplementedError()  # pragma: no cover

    def request_choose(self, *args, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def build_task(self):
        raise NotImplementedError()  # pragma: no cover

    def setup_task_for_token(self, task):
        self._env.social_broker.set_response_value(
            'get_task_by_token',
            self._env.social_broker.get_task_by_token_response(**task),
        )

    def setup_track(self, **kwargs):
        self._env.track_manager.create_test_track(
            self._env.track_manager.get_manager(),
            'authorize',
        )

        defaults = dict(
            social_task_id=TEST_SOCIAL_TASK_ID1,
            social_output_mode=None,
            social_return_brief_profile=False,
            social_place=None,
            retpath=TEST_RETPATH1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        with self._env.track_manager.get_manager().transaction(TEST_TRACK_ID1).rollback_on_error() as track:
            for key in kwargs:
                if kwargs[key] is not None:
                    setattr(track, key, kwargs[key])

    def setup_task_for_track(self, task):
        with self._env.track_manager.get_manager().transaction(TEST_TRACK_ID1).rollback_on_error() as track:
            track.social_task_data = task_data_response(**task)

    def setup_task_for_task_id(self, task):
        self._env.social_api.set_response_value('get_task_data', task_data_response(**task))

    def setup_social_profiles(self, profiles):
        self._env.social_api.set_response_value('get_profiles', get_profiles_response(profiles))

    def build_social_profile(self, uid=TEST_UID1, allow_auth=True, **kwargs):
        profile = dict(kwargs)
        profile.update(
            dict(
                uid=uid,
                allow_auth=allow_auth,
            ),
        )
        return profile

    def setup_yandex_accounts(
        self,
        profile_accounts=Undefined,
        email_account=Undefined,
    ):
        """
        Входные параметры

        profile_accounts -- аккаунты с привязанным соц. профиль, которым входит
            пользователь.

        email_account -- аккаунт с алиасом равным e-mail'у из соц. профиля,
            которым входит пользователь.
        """
        responses = list()

        if profile_accounts is not Undefined:
            responses.append(blackbox_userinfo_response_multiple(profile_accounts))

        if email_account is None:
            responses.append(blackbox_userinfo_response(uid=None))
        elif email_account:
            responses.append(blackbox_userinfo_response(**email_account))

        if responses:
            self._env.blackbox.set_response_side_effect('userinfo', responses)

    def setup_profile_creation(self):
        self._env.social_api.set_response_value('bind_task_profile', get_bind_response())

    def setup_yandex_token_generation(self, token=TEST_YANDEX_TOKEN1):
        self._env.oauth.set_response_value(
            '_token',
            token_response(access_token=token),
        )

    def setup_yandex_auth_code_generation(self, code):
        self._env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code=code),
        )

    def setup_session_generation(self):
        self._env.blackbox.set_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self._env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self._env.blackbox.set_response_value('sign', blackbox_sign_response())

    def build_yandex_phonish_account(self, **kwargs):
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        phonish_phone = build_phone_bound(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
            phone_confirmed=datetime.now(),
            binding_flags=binding_flags,
        )

        defaults = dict(
            uid=TEST_UID1,
            login=TEST_PHONISH_LOGIN1,
            phonish_alias=TEST_PHONISH_LOGIN1,
            phonish_phone=phonish_phone,
        )

        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        userinfo_args = dict(**kwargs)

        phonish_alias = userinfo_args.pop('phonish_alias')
        if phonish_alias:
            userinfo_args = deep_merge(userinfo_args, dict(aliases=dict(phonish=phonish_alias)))

        phonish_phone = userinfo_args.pop('phonish_phone')
        if phonish_phone:
            userinfo_args = deep_merge(userinfo_args, phonish_phone)

        return userinfo_args

    def build_yandex_mailish_account(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            login=TEST_MAILISH_LOGIN1,
            mailish_alias=TEST_MAILISH_LOGIN1,
        )

        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        userinfo_args = dict(**kwargs)

        mailish_alias = userinfo_args.pop('mailish_alias')
        if mailish_alias:
            userinfo_args = deep_merge(userinfo_args, dict(aliases=dict(mailish=mailish_alias)))

        return userinfo_args

    def setup_login_available_for_registration(self, login=TEST_SOCIAL_LOGIN1):
        self._fake_social_login_generator.set_return_value(login)
        self._env.blackbox.set_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({login: 'free'}),
        )

    def build_yandex_social_account(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            login=TEST_SOCIAL_LOGIN1,
            social_alias=TEST_SOCIAL_LOGIN1,
            has_social_subscription=True,
            display_name=self.build_social_display_name(),
        )

        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        userinfo_args = dict(**kwargs)

        social_alias = userinfo_args.pop('social_alias')
        if social_alias:
            userinfo_args = deep_merge(userinfo_args, dict(aliases=dict(social=social_alias)))

        if userinfo_args.pop('has_social_subscription'):
            userinfo_args = deep_merge(userinfo_args, dict(subscribed_to=[Service.by_slug('social')]))

        return userinfo_args

    def build_social_display_name(self):
        return dict(
            name='Firstname Lastname',
            social=dict(provider='gg', profile_id=123456789),
        )

    def build_yandex_full_account(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            portal_alias=TEST_LOGIN1,
            display_name=self.build_full_display_name(),
            crypt_password=TEST_PASSWORD_HASH1,
        )

        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        userinfo_args = dict(**kwargs)

        portal_alias = userinfo_args.pop('portal_alias')
        if portal_alias:
            userinfo_args = deep_merge(userinfo_args, dict(aliases=dict(portal=portal_alias)))

        if userinfo_args.pop('sms_2fa_on', None):
            userinfo_args = deep_merge(
                userinfo_args,
                dict(attributes={'account.sms_2fa_on': '1'}),
            )

        return userinfo_args

    def build_full_display_name(self, default_avatar=None):
        display_name = dict(name=TEST_LOGIN1)
        if default_avatar is not None:
            display_name.update(default_avatar=default_avatar)
        return display_name

    def build_yandex_lite_account(self, **kwargs):
        email_login, email_domain = TEST_EMAIL1.split('@')
        defaults = dict(
            crypt_password=TEST_PASSWORD_HASH1,
            default_avatar_key=TEST_DEFAULT_AVATAR1,
            display_name=self.build_lite_display_name(),
            display_login=TEST_DISPLAY_LOGIN1,
            emails=[
                self._env.email_toolkit.create_validated_external_email(email_login, email_domain, default=True),
            ],
            lite_alias=TEST_EMAIL1,
            login=TEST_EMAIL1,
            uid=TEST_UID1,
        )

        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        userinfo_args = dict(**kwargs)

        lite_alias = userinfo_args.pop('lite_alias')
        if lite_alias:
            userinfo_args = deep_merge(userinfo_args, dict(aliases=dict(lite=lite_alias)))

        return userinfo_args

    def build_lite_display_name(self, default_avatar=None):
        display_name = dict(name=TEST_EMAIL1)
        if default_avatar is not None:
            display_name.update(default_avatar=default_avatar)
        return display_name

    def build_headers(self, **kwargs):
        defaults = dict(
            user_ip=TEST_USER_IP1,
            accept_language='ru',
            user_agent='curl',
            host='',
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return mock_headers(**kwargs)

    def build_web_headers(self, **kwargs):
        defaults = dict(
            host='passport.yandex.ru',
            cookie=self.build_cookies(),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return self.build_headers(**kwargs)

    def build_cookies(self):
        return 'yandexuid=%s' % TEST_YANDEXUID1

    def build_ok_response(self, **kwargs):
        defaults = merge_dicts(
            self._build_base_response(),
            dict(
                has_enabled_accounts=True,
                account=self.get_account_response(),
                profile_id=123456789,
            ),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return remove_none_values(kwargs)

    def build_auth_not_allowed_response(self, **kwargs):
        profile_response = dict(self.get_profile_response())
        profile_response.update(email=PROFILE_EMAIL)
        defaults = merge_dicts(
            self._build_base_response(),
            dict(
                has_enabled_accounts=True,
                profile=profile_response,
                return_brief_profile=None,
            ),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return remove_none_values(kwargs)

    def build_auth_response(self, **kwargs):
        return self.build_ok_response(state='auth', **kwargs)

    def build_register_response(self, **kwargs):
        defaults = merge_dicts(
            self._build_base_response(),
            dict(
                account=None,
                has_enabled_accounts=False,
                profile_id=None,
            ),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return self.build_ok_response(state='register', **kwargs)

    def build_suggest_response(self, **kwargs):
        defaults = merge_dicts(
            self._build_base_response(),
            dict(
                account=None,
                has_enabled_accounts=False,
                profile_id=None,
            ),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return self.build_ok_response(state='suggest', **kwargs)

    def build_error_response(self, **kwargs):
        defaults = merge_dicts(
            self._build_base_response(),
            dict(
                has_enabled_accounts=True,
                account=self.get_account_response(),
                profile_id=123456789,
            ),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return remove_none_values(kwargs)

    def get_account_response(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            login=TEST_SOCIAL_LOGIN1,
            display_name=self.build_social_display_name(),
            is_pdd=False,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return kwargs

    def get_suggested_account_response(self, **kwargs):
        display_name = self.build_full_display_name(
            default_avatar=kwargs.pop('default_avatar', TEST_DEFAULT_AVATAR1),
        )
        defaults = dict(
            default_email=TEST_YANDEX_EMAIL1,
            display_login=TEST_DISPLAY_LOGIN1,
            display_name=display_name,
            login=TEST_LOGIN1,
            uid=TEST_UID1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return remove_none_values(kwargs)

    def get_suggested_lite_response(self, **kwargs):
        defaults = dict(
            default_email=TEST_EMAIL1,
            display_login=TEST_EMAIL1,
            display_name=self.build_lite_display_name(default_avatar=TEST_DEFAULT_AVATAR1),
            login=TEST_EMAIL1,
        )
        kwargs = merge_dicts(defaults, kwargs)
        return self.get_suggested_account_response(**kwargs)

    def _build_base_response(self):
        return dict(
            track_id=TEST_TRACK_ID1,
            retpath=TEST_RETPATH1,
            return_brief_profile=False,
            is_native=True,
            provider=self.get_provider_response(),
            profile=self.get_profile_response(),
        )

    def get_provider_response(self):
        return dict(id=5, code='gg', name='google')

    def setup_statbox_templates(self):
        setup_statbox_templates(self._env.statbox)
        self._env.statbox.bind_entry(
            'native_start_submitted',
            _inherit_from=['submitted'],
            _exclude=['yandexuid', 'broker_consumer'],
            type='social_native',
            application=str(TEST_APPLICATION_ID1),
            ip=TEST_USER_IP1,
            host='',
        )
        self._env.statbox.bind_entry(
            'callback_end',
            state='auth',
            accounts=str(TEST_UID1),
            enabled_accounts_count='1',
            disabled_accounts_count='0',
        )
        self._env.statbox.bind_entry(
            'auth',
            uid=str(TEST_UID1),
            login=TEST_SOCIAL_LOGIN1,
            ip=TEST_USER_IP1,
        )

    def get_profile_response(self):
        return dict(
            userid='57575757575',
            provider=dict(code='gg', id=5, name='google'),
            username='some.user',
            firstname='Firstname',
            lastname='Lastname',
            gender='m',
            email=TEST_YANDEX_EMAIL1,
            links=['https://plus.google.com/118320684662584130204'],
            avatar={'0x0': TEST_AVATAR_URL},
        )

    def setup_frodo_check(self):
        self._env.frodo.set_response_value('check', '<spamlist></spamlist>')

    def assert_social_account_exists(self):
        self._env.db.check('aliases', 'social', TEST_SOCIAL_LOGIN1, uid=1, db='passportdbcentral')
        self._env.db.check_missing('aliases', 'portal', uid=1, db='passportdbcentral')

        self._env.db.check_db_attr(1, 'account.registration_datetime', TimeNow())
        self._env.db.check_db_attr(1, 'account.display_name', 's:123456789:gg:Firstname Lastname')
        self._env.db.check_db_attr(1, 'person.firstname', 'Firstname')
        self._env.db.check_db_attr(1, 'person.lastname', 'Lastname')
        self._env.db.check_db_attr(1, 'person.gender', 'm')

        EmailDatabaseMatcher(
            db_faker=self._env.db,
            uid=1,
            email=Email(
                id=1,
                address=TEST_YANDEX_EMAIL1,
                created_at=DatetimeNow(),
                confirmed_at=DatetimeNow(),
                bound_at=DatetimeNow(),
                is_unsafe=True,
                is_rpop=False,
                is_silent=False,
            ),
        ).match_all()

        self._env.db.check_db_attr_missing(1, 'password.encrypted')

    def assert_avatars_log_written(self):
        self._env.avatars_logger.assert_has_written([
            self._env.avatars_logger.entry(
                'base',
                uid='1',
                avatar_to_upload=TEST_AVATAR_URL,
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip=TEST_USER_IP1,
                skip_if_set='0',
            ),
        ])


class ThirdPartyTestBuilder(TestBuilder):
    def request_native_start(self, headers=None):
        if headers is None:
            headers = self.build_headers()
        return self._env.client.post(
            '/1/bundle/auth/social/third_party_native_start/',
            query_string={'consumer': 'dev'},
            data={
                'provider_token': TEST_PROVIDER_TOKEN1,
                'provider': 'gg',
                'application': TEST_APPLICATION_ID1,
                'retpath': TEST_RETPATH1,
            },
            headers=headers,
        )

    def request_choose(self, uid=TEST_UID1, track_id=TEST_TRACK_ID1, headers=None):
        if headers is None:
            headers = self.build_headers()
        return self._env.client.post(
            '/1/bundle/auth/social/third_party_choose/',
            query_string={'consumer': 'dev'},
            data={
                'track_id': track_id,
                'uid': uid,
            },
            headers=headers,
        )

    def request_register(self, headers=None):
        if headers is None:
            headers = self.build_headers()

        return self._env.client.post(
            '/1/bundle/auth/social/third_party_register/',
            query_string={'consumer': 'dev'},
            data={
                'track_id': TEST_TRACK_ID1,
                'eula_accepted': '1',
            },
            headers=headers,
        )

    def build_task(self, **kwargs):
        defaults = dict(
            app_party=APP_PARTY_3RD_PARTY,
            email=TEST_YANDEX_EMAIL1,
            related_yandex_client_id=TEST_YANDEX_CLIENT_ID1,
            related_yandex_client_secret=TEST_YANDEX_CLIENT_SECRET1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return kwargs

    def setup_statbox_templates(self):
        super(ThirdPartyTestBuilder, self).setup_statbox_templates()
        self._env.statbox.bind_entry(
            'callback_end',
            third_party_app='1',
        )


class PrimaryTestBuilder(TestBuilder):
    def request_callback(self, status='ok', task_id=TEST_SOCIAL_TASK_ID1,
                         track_id=TEST_TRACK_ID1, headers=None):
        if headers is None:
            headers = self.build_web_headers()

        return self._env.client.post(
            '/1/bundle/auth/social/callback/',
            query_string={'consumer': 'dev'},
            data={
                'track_id': track_id,
                'status': status,
                'task_id': task_id,
            },
            headers=headers,
        )

    def request_native_start(
        self,
        headers=None,
        process_uuid=None,
        retpath=TEST_RETPATH1,
        broker_consumer=TEST_CONSUMER1,
    ):
        if headers is None:
            headers = self.build_headers()

        data = {
            'provider_token': TEST_PROVIDER_TOKEN1,
            'provider': 'gg',
            'application': TEST_APPLICATION_ID1,
            'retpath': retpath,
            'broker_consumer': broker_consumer,
            'process_uuid': process_uuid,
        }

        return self._env.client.post(
            '/1/bundle/auth/social/native_start/',
            query_string={'consumer': 'dev'},
            data=data,
            headers=headers,
        )

    def request_choose(self, uid=TEST_UID1, track_id=TEST_TRACK_ID1, headers=None):
        if headers is None:
            headers = self.build_headers()

        return self._env.client.post(
            '/1/bundle/auth/social/choose/',
            query_string={'consumer': 'dev'},
            data={
                'track_id': track_id,
                'uid': uid,
            },
            headers=headers,
        )

    def request_register(self, headers=None):
        if headers is None:
            headers = self.build_headers()

        return self._env.client.post(
            '/1/bundle/auth/social/register/',
            query_string={'consumer': 'dev'},
            data={
                'track_id': TEST_TRACK_ID1,
                'eula_accepted': '1',
            },
            headers=headers,
        )

    def build_task(self, **kwargs):
        defaults = dict(
            app_party=APP_PARTY_YANDEX,
            email=TEST_YANDEX_EMAIL1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return kwargs

    def build_auth_response(self, token=None, **kwargs):
        return super(PrimaryTestBuilder, self).build_auth_response(x_token=token, token=token, **kwargs)

    def setup_statbox_templates(self):
        super(PrimaryTestBuilder, self).setup_statbox_templates()
        self._env.statbox.bind_entry(
            'callback_begin',
            task_id=TEST_SOCIAL_TASK_ID1,
        )
        self._env.statbox.bind_entry(
            'cookie_set',
            _exclude=['consumer'],
            uid=str(TEST_UID1),
            input_login=TEST_SOCIAL_LOGIN1,
            person_country='ru',
            ip=TEST_USER_IP1,
            ip_country='us',
            yandexuid=TEST_YANDEXUID1,
        )

    def setup_track(self, **kwargs):
        kwargs.setdefault('social_broker_consumer', TEST_CONSUMER1)
        super(PrimaryTestBuilder, self).setup_track(**kwargs)

    def _build_base_response(self):
        response = super(PrimaryTestBuilder, self)._build_base_response()
        response.update(broker_consumer=TEST_CONSUMER1)
        return response
