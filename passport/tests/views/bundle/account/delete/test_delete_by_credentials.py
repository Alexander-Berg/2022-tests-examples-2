# -*- coding: utf-8 -*-

import abc

import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_oauth_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.builders.social_api.faker.social_api import get_profiles_response
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_FAMILY_ID1,
    TEST_LOGIN1,
    TEST_OAUTH_CLIENT_ID1,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER1,
    TEST_SOCIAL_LOGIN1,
    TEST_UID1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
    TEST_YANDEX_TOKEN1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import deep_merge


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env, response_dict):
        self._env = env
        self._kwargs = dict()
        self._response_dict = response_dict

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_userinfo_response(**self.kwargs)
        self._response_dict[self.kwargs.get('uid')] = response
        self._env.db.serialize(response)


class PhoneBlackboxResponseMixin(object):
    def add_phone(self):
        kwargs = deep_merge(
            self.kwargs,
            build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
        )
        self.kwargs.clear()
        self.kwargs.update(kwargs)


class OauthBlackboxResponse(
    PhoneBlackboxResponseMixin,
    IBlackboxResponse,
):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @classmethod
    def from_userinfo(cls, userinfo_response, env):
        self = cls(env)
        self.kwargs.update(deep_merge(
            userinfo_response.kwargs,
            dict(
                scope=X_TOKEN_OAUTH_SCOPE,
            ),
        ))
        return self

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_oauth_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('oauth', [response])
        self._env.db.serialize(response, 'oauth')


class SocialUserinfoBlackboxResponse(UserinfoBlackboxResponse):
    def __init__(self, env):
        super(SocialUserinfoBlackboxResponse, self).__init__(env, dict())
        kwargs = deep_merge(
            self.kwargs,
            dict(
                aliases=dict(social=TEST_SOCIAL_LOGIN1),
                subscribed_to=[Service.by_slug('social')],
                uid=TEST_UID1,
            ),
        )
        self.kwargs.clear()
        self.kwargs.update(kwargs)


class MtsSocialUserinfoBlackboxResponse(
    PhoneBlackboxResponseMixin,
    SocialUserinfoBlackboxResponse,
):
    def __init__(self, env):
        super(MtsSocialUserinfoBlackboxResponse, self).__init__(env)
        self.add_phone()


class MtsSocialOauthBlackboxResponse(OauthBlackboxResponse):
    def __init__(self, env):
        super(MtsSocialOauthBlackboxResponse, self).__init__(env)
        self._kwargs = OauthBlackboxResponse.from_userinfo(MtsSocialUserinfoBlackboxResponse(env), env).kwargs


class SocialGetProfilesResponse(object):
    def __init__(self, env):
        self._env = env
        self._profiles = list()

    @classmethod
    def with_mts(cls, env):
        self = cls(env)
        self._profiles.extend([dict(
            provider_code='mt',
            uid=TEST_UID1,
        )])
        return self

    @classmethod
    def with_vk(cls, env):
        self = cls(env)
        self._profiles.extend([dict(
            provider_code='vk',
            uid=TEST_UID1,
        )])
        return self

    @property
    def profiles(self):
        return self._profiles

    def setup(self):
        response = get_profiles_response(self.profiles)
        self._env.social_api.extend_response_side_effect('get_profiles', [response])


class SocialDeleteAllProfilesByUidResponse(object):
    def __init__(self, env):
        self._env = env

    def setup(self):
        self._env.social_api.extend_response_side_effect('delete_all_profiles_by_uid', [dict()])


class BaseAccountDeleteByCredentialsTestEnv(object):
    def setup(self):
        self.setup_oauth()
        self.setup_family_info()
        self.setup_husky_api()
        self.setup_get_profiles()
        self.setup_delete_all_profiles_by_uid()

    def setup_oauth(self):
        pass

    def setup_family_info(self):
        pass

    def setup_husky_api(self):
        pass

    def setup_get_profiles(self):
        pass

    def setup_delete_all_profiles_by_uid(self):
        pass


class MtsAccountDeleteByCredentialsTestEnv(BaseAccountDeleteByCredentialsTestEnv):
    def __init__(self, env):
        super(MtsAccountDeleteByCredentialsTestEnv, self).__init__()

        self.oauth_response = MtsSocialOauthBlackboxResponse(env)
        self.oauth_response.kwargs.update(client_id=TEST_OAUTH_CLIENT_ID1)

        self.get_profiles_response = SocialGetProfilesResponse.with_mts(env)
        self.delete_all_profiles_by_uid_response = SocialDeleteAllProfilesByUidResponse(env)

    def setup_oauth(self):
        self.oauth_response.setup()

    def setup_get_profiles(self):
        self.get_profiles_response.setup()

    def setup_delete_all_profiles_by_uid(self):
        self.delete_all_profiles_by_uid_response.setup()


@with_settings_hosts(
    OAUTH_APPLICATIONS_FOR_MUSIC=dict(mt=dict(client_id=TEST_OAUTH_CLIENT_ID1)),
)
class TestAccountDeleteByCredentialsView(BaseBundleTestViews):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/delete_account/by_credentials/'
    http_method = 'POST'
    http_headers = dict(
        authorization='OAuth ' + TEST_YANDEX_TOKEN1,
        user_ip=TEST_USER_IP1,
        user_agent=TEST_USER_AGENT1,
    )

    def setUp(self):
        super(TestAccountDeleteByCredentialsView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            {
                self.consumer: {
                    'grants': {'account': 'delete_by_credentials'},
                    'networks': ['127.0.0.1'],
                },
            },
        )

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        super(TestAccountDeleteByCredentialsView, self).tearDown()

    def assert_ok_blackbox_oauth_request(self, request):
        request.assert_query_contains(dict(
            aliases='all_with_hidden',
            get_family_info='yes',
            method='oauth',
            oauth_token=TEST_YANDEX_TOKEN1,
            userip=TEST_USER_IP1,
        ))
        request.assert_contains_attributes([
            'account.is_disabled',
        ])
        request.assert_has_all_subscriptions()

    def assert_ok_blackbox_family_info_request(self, request):
        request.assert_query_contains(dict(
            family_id=TEST_FAMILY_ID1,
            get_members_info='all',
            get_place='yes',
            method='family_info',
        ))

    def assert_ok_social_get_profiles_request(self, request):
        request.assert_url_starts_with('https://api.social-test.yandex.ru/api/profiles?')
        request.assert_query_contains(dict(uid=str(TEST_UID1)))

    def assert_ok_social_delete_all_profiles_by_uid_request(self, request):
        request.assert_properties_equal(method='DELETE')
        request.assert_url_starts_with('https://api.social-test.yandex.ru/api/user/%s?' % TEST_UID1)

    def assert_ok_account_delete_by_credentials_db(self):
        uid = TEST_UID1
        shard_db_name = 'passportdbshard1'

        for table, db in (
            ('attributes', shard_db_name),
            ('extended_attributes', shard_db_name),
            ('aliases', 'passportdbcentral'),
            ('password_history', shard_db_name),
            ('passman_recovery_keys', shard_db_name),
        ):
            records_found = self.env.db.select(table, db=db, uid=uid)
            assert not records_found, records_found

        self.env.db.check_table_contents(
            'phone_bindings_history_delete_tasks',
            'passportdbcentral',
            [
                {
                    'task_id': 1,
                    'uid': uid,
                    'deletion_started_at': mock.ANY,
                },
            ],
        )

        self.env.db.check(
            'reserved_logins',
            'login',
            TEST_SOCIAL_LOGIN1,
            db='passportdbcentral',
        )

    def assert_ok_account_disabled_by_credentials_db(self):
        self.env.db.check_db_attr(TEST_UID1, 'account.is_disabled', str(ACCOUNT_DISABLED_ON_DELETION))

    def assert_ok_family_delete_by_credentials_db(
        self,
        family_id=None,
        member_uids=None,
        is_admin=True,
    ):
        family_id = family_id or TEST_FAMILY_ID1
        member_uids = member_uids or [TEST_UID1]

        for uid in member_uids:
            records_found = self.env.db.select(
                'family_members',
                db='passportdbcentral',
                uid=uid,
                family_id=str(family_id).lstrip('f'),
            )
            assert not records_found, records_found

        records_found = self.env.db.select(
            'family_info',
            db='passportdbcentral',
            family_id=int(str(family_id).lstrip('f')),
        )
        assert len(records_found) == 1 - int(is_admin)

    def assert_ok_delete_by_credentials_statbox(self, extra_lines=None):
        expected = extra_lines or dict()
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        def opt(name):
            if name in expected:
                lines.append(self.env.statbox.entry(name))

        req('submitted')
        opt('family.admin_uid')
        opt('family.members.' + str(TEST_UID1))
        req('account.global_logout_datetime')
        req('account.revoker.tokens')
        req('account.revoker.web_sessions')
        req('account.revoker.app_passwords')
        req('account.disabled_status')
        req('aliases.social')
        req('person.firstname')
        req('person.lastname')
        req('person.language')
        req('person.country')
        req('person.gender')
        req('person.birthday')
        req('person.fullname')
        req('frodo_karma')
        req('subscription.passport')
        opt('subscription.mail')
        req('subscription.social')
        req('deleted')

        self.env.statbox.assert_equals(lines)

    def assert_ok_account_disabled_by_credentials_statbox(self, extra_lines=None):
        expected = extra_lines or dict()
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        def opt(name):
            if name in expected:
                lines.append(self.env.statbox.entry(name))

        req('submitted')
        req('blocked_on_delete')
        req('account.disabled_on_delete')

        self.env.statbox.assert_equals(lines)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base_request',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'base_attr_deleted',
            _inherit_from=['account_modification', 'base_request'],
            entity='-',
            new='-',
            old='-',
            operation='deleted',
        )
        self.env.statbox.bind_entry(
            'base_family_attr_deleted',
            _inherit_from=['base_request'],
            entity='-',
            event='family_info_modification',
            new='-',
            old='-',
            operation='deleted',
        )
        mode = 'account_delete'

        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['base_request'],
            action='submitted',
            mode=mode,
        )

        self.env.statbox.bind_entry(
            'family.admin_uid',
            _inherit_from=['base_family_attr_deleted'],
            entity='admin_uid',
            family_id=TEST_FAMILY_ID1,
            old=mock.ANY,
        )
        self.env.statbox.bind_entry(
            'family.members.' + str(TEST_UID1),
            _inherit_from=['base_family_attr_deleted'],
            attribute='members.%s.uid' % TEST_UID1,
            entity='members',
            entity_id=str(TEST_UID1),
            family_id=TEST_FAMILY_ID1,
            old=mock.ANY,
        )

        self.env.statbox.bind_entry(
            'aliases.social',
            _inherit_from=['account_modification', 'base_request'],
            entity='aliases',
            operation='removed',
            type=str(EavSerializer.alias_name_to_type('social')),
            uid=str(TEST_UID1),
        )

        attrs = [
            'account.disabled_status',
            'account.global_logout_datetime',
            'account.revoker.app_passwords',
            'account.revoker.tokens',
            'account.revoker.web_sessions',
            'person.birthday',
            'person.country',
            'person.firstname',
            'person.fullname',
            'person.gender',
            'person.language',
            'person.lastname',
        ]
        for key in attrs:
            self.env.statbox.bind_entry(
                key,
                _inherit_from=['base_attr_deleted'],
                entity=key,
                old=mock.ANY,
                uid=str(TEST_UID1),
            )

        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'base_request'],
            action='account_delete',
            login=TEST_SOCIAL_LOGIN1,
            new='-',
            old='0',
            registration_datetime='-',
            uid=str(TEST_UID1),
        )

        for slug in [
            'mail',
            'passport',
            'social',
        ]:
            self.env.statbox.bind_entry(
                'subscription.' + slug,
                _inherit_from=['subscriptions', 'base_request'],
                operation='removed',
                sid=str(Service.by_slug(slug).sid),
                uid=str(TEST_UID1),
            )

        self.env.statbox.bind_entry(
            'subscription.mail',
            _inherit_from=['subscription.mail'],
            suid='1',
        )

        self.env.statbox.bind_entry(
            'deleted',
            _inherit_from=['base_request'],
            action='deleted',
            mode=mode,
        )

        self.env.statbox.bind_entry(
            'blocked_on_delete',
            _inherit_from=['base_request'],
            action='blocked_on_delete',
            mode=mode,
        )

        self.env.statbox.bind_entry(
            'account.disabled_on_delete',
            _inherit_from=['account.disabled_status'],
            new='disabled_on_deletion',
            operation='updated',
        )

    def assert_ok_delete_by_credentials_event_log(self, events=None):
        events = dict(events) if events else dict()

        defaults = {
            'info.login': TEST_SOCIAL_LOGIN1,
            'sid.rm': self.format_sid_list([
                ('passport', 'test'),
                ('social', TEST_SOCIAL_LOGIN1),
            ]),
        }
        for name in defaults:
            if name not in events:
                events[name] = defaults[name]

        e = EventCompositor(uid=str(TEST_UID1))

        def opt(name):
            if name in events:
                e(name, events[name])

        if 'family_admin' in events:
            with e.prefix('family.%s.' % TEST_FAMILY_ID1):
                e('family_admin', '-')
                e('family_member', '-')
            e('action', 'family_admin_account_delete')
            e('consumer', TEST_CONSUMER1)
            e('user_agent', TEST_USER_AGENT1)

        e('info.login', events['info.login'])
        e('info.ena', '-')
        e('info.disabled_status', '-')
        e('info.glogout', '-')
        e('info.tokens_revoked', '-')
        e('info.web_sessions_revoked', '-')
        e('info.app_passwords_revoked', '-')
        e('info.firstname', '-')
        e('info.lastname', '-')
        e('info.sex', '-')
        e('info.birthday', '-')
        e('info.city', '-')
        e('info.country', '-')
        e('info.tz', '-')
        e('info.lang', '-')
        e('info.password', '-')
        e('info.password_quality', '-')
        e('info.password_update_time', '-')
        e('info.totp', mock.ANY)
        e('info.totp_update_time', '-')
        e('info.rfc_totp', mock.ANY)
        e('info.karma_prefix', '-')
        e('info.karma_full', '-')
        e('info.karma', '-')
        opt('sid.rm.info')
        opt('mail.rm')
        e('sid.rm', events['sid.rm'])

        with e.context('phone.%s.' % TEST_PHONE_ID1):
            e('action', 'deleted')
            e('number', TEST_PHONE_NUMBER1.e164)

        e('action', 'account_delete')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_account_disabled_by_credentials_event_log(self, events=None):
        events = dict(events) if events else dict()

        e = EventCompositor(uid=str(TEST_UID1))

        def opt(name):
            if name in events:
                e(name, events[name])

        e('info.ena', '0')
        e('info.disabled_status', str(ACCOUNT_DISABLED_ON_DELETION))

        e('action', 'account_delete')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    @staticmethod
    def format_sid_list(sids):
        return ','.join('%s|%s' % (Service.by_slug(s), n) for s, n, in sids)

    def test_mts(self):
        MtsAccountDeleteByCredentialsTestEnv(self.env).setup()

        rv = self.make_request()

        self.assert_ok_response(rv)

        assert len(self.env.blackbox.requests) == 1
        self.assert_ok_blackbox_oauth_request(self.env.blackbox.requests[0])

        self.assert_ok_account_delete_by_credentials_db()
        self.assert_ok_delete_by_credentials_statbox()
        self.assert_ok_delete_by_credentials_event_log()

        assert len(self.env.social_api.requests) == 2
        self.assert_ok_social_get_profiles_request(self.env.social_api.requests[0])
        self.assert_ok_social_delete_all_profiles_by_uid_request(self.env.social_api.requests[1])

    def test_family_admin(self):
        env = MtsAccountDeleteByCredentialsTestEnv(self.env)
        env.oauth_response.kwargs.update(
            family_info=dict(
                admin_uid=TEST_UID1,
                family_id=TEST_FAMILY_ID1,
            ),
        )
        env.setup_family_info = lambda: self.env.blackbox.extend_response_side_effect(
            'family_info', [
                blackbox_family_info_response(
                    family_id=TEST_FAMILY_ID1,
                    admin_uid=str(TEST_UID1),
                    uids=[TEST_UID1],
                    with_members_info=True,
                ),
            ],
        )
        env.setup()

        rv = self.make_request()

        self.assert_ok_response(rv)

        assert len(self.env.blackbox.requests) == 2
        self.assert_ok_blackbox_oauth_request(self.env.blackbox.requests[0])
        self.assert_ok_blackbox_family_info_request(self.env.blackbox.requests[1])

        self.assert_ok_account_delete_by_credentials_db()
        self.assert_ok_family_delete_by_credentials_db()

        self.assert_ok_delete_by_credentials_statbox(extra_lines=[
            'family.admin_uid',
            'family.members.' + str(TEST_UID1),
        ])
        self.assert_ok_delete_by_credentials_event_log(events={
            'family_admin': '-',
        })

        assert len(self.env.social_api.requests) == 2
        self.assert_ok_social_get_profiles_request(self.env.social_api.requests[0])
        self.assert_ok_social_delete_all_profiles_by_uid_request(self.env.social_api.requests[1])

    def test_has_mail(self):
        env = MtsAccountDeleteByCredentialsTestEnv(self.env)
        env.oauth_response.kwargs['subscribed_to'].append(Service.by_slug('mail'))
        env.setup_husky_api = lambda: self.env.husky_api.extend_response_side_effect(
            'delete_user',
            [husky_delete_user_response()],
        )
        env.setup()

        rv = self.make_request()

        self.assert_ok_response(rv)

        assert len(self.env.blackbox.requests) == 1
        self.assert_ok_blackbox_oauth_request(self.env.blackbox.requests[0])

        self.assert_ok_account_delete_by_credentials_db()

        self.env.statbox.bind_entry('frodo_karma', _inherit_from=['frodo_karma'], suid='1')
        self.assert_ok_delete_by_credentials_statbox(extra_lines=['subscription.mail'])

        self.assert_ok_delete_by_credentials_event_log(events={
            'sid.rm.info': '%s|%s|1' % (TEST_UID1, TEST_SOCIAL_LOGIN1),
            'mail.rm': '1',
            'sid.rm': self.format_sid_list([
                ('passport', 'test'),
                ('mail', TEST_SOCIAL_LOGIN1),
                ('social', TEST_SOCIAL_LOGIN1),
            ]),
        })

        assert len(self.env.social_api.requests) == 2
        self.assert_ok_social_get_profiles_request(self.env.social_api.requests[0])
        self.assert_ok_social_delete_all_profiles_by_uid_request(self.env.social_api.requests[1])

    def test_has_blocking_sid(self):
        env = MtsAccountDeleteByCredentialsTestEnv(self.env)
        blocking_service = Service.by_slug('slova')
        env.oauth_response.kwargs['subscribed_to'].append(blocking_service)
        env.setup()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.has_blocking_sids'],
            blocking_sids=[blocking_service.sid],
        )

        self.assert_ok_account_disabled_by_credentials_db()
        self.assert_ok_account_disabled_by_credentials_statbox()
        self.assert_ok_account_disabled_by_credentials_event_log()

        assert len(self.env.social_api.requests) == 1
        self.assert_ok_social_get_profiles_request(self.env.social_api.requests[0])

    def test_completed_mts(self):
        env = MtsSocialOauthBlackboxResponse(self.env)
        env.kwargs['aliases'].update(portal=TEST_LOGIN1)
        env.setup()

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_vk(self):
        env = MtsAccountDeleteByCredentialsTestEnv(self.env)
        env.get_profiles_response = SocialGetProfilesResponse.with_vk(self.env)
        env.setup()

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])
