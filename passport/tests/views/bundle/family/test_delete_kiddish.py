# -*- coding: utf-8 -*-

import abc
from datetime import datetime

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID,
    TEST_FAMILY_ID1,
    TEST_HOST,
    TEST_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_COOKIE,
)
from passport.backend.api.views.bundle.constants import (
    FAMILY_MANAGE_SCOPE,
    SESSIONID_SCOPE,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.test.consts import (
    TEST_BIRTHDATE1,
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_DEFAULT_AVATAR1,
    TEST_FIRSTNAME1,
    TEST_KIDDISH_LOGIN1,
    TEST_KIDDISH_LOGIN2,
    TEST_LASTNAME1,
    TEST_LOGIN1,
    TEST_REGISTRAION_DATETIME1,
    TEST_UID2,
    TEST_UID3,
    TEST_UID4,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
    TEST_USER_TICKET1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.gender import Gender
from passport.backend.utils.common import (
    classproperty,
    merge_dicts,
)
from passport.backend.utils.string import smart_text


TEST_CONTENT_RATING_CLASS1 = 2
TEST_DISPLAY_NAME1 = DisplayName(u'Попосерик2020')


@with_settings_hosts()
class BaseDeleteKiddishTestCase(BaseFamilyTestcase):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/family/delete_kiddish/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_agent': TEST_USER_AGENT1,
        'user_ip': TEST_USER_IP1,
    }
    http_method = 'POST'

    def setUp(self):
        super(BaseDeleteKiddishTestCase, self).setUp()

        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    grants={
                        'family': [
                            'delete_kiddish',
                            'delete_kiddish_by_uid',
                        ],
                    },
                    networks=[TEST_CONSUMER_IP1],
                ),
            },
        )

    def setup_statbox_templates(self):
        super(BaseDeleteKiddishTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'base_request',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT1,
        )

        self.env.statbox.bind_entry(
            'base_attr_deleted',
            _inherit_from=['account_modification', 'base_request'],
            new='-',
            old='-',
            operation='deleted',
        )

        attrs = {
            'account.content_rating_class': str(TEST_CONTENT_RATING_CLASS1),
            'person.birthday': TEST_BIRTHDATE1,
            'person.country': 'ru',
            'person.default_avatar': TEST_DEFAULT_AVATAR1,
            'person.display_name': smart_text(TEST_DISPLAY_NAME1),
            'person.firstname': smart_text(TEST_FIRSTNAME1),
            'person.fullname': smart_text('%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1)),
            'person.gender': Gender.to_char(Gender.Male),
            'person.language': 'ru',
            'person.lastname': smart_text(TEST_LASTNAME1),
        }
        for key in attrs:
            self.env.statbox.bind_entry(
                key,
                _inherit_from=['base_attr_deleted'],
                entity=key,
                old=attrs[key],
                uid=str(TEST_UID2),
            )

        self.env.statbox.bind_entry(
            'account.kiddish',
            _inherit_from=['account_modification', 'base_request'],
            entity='aliases',
            operation='removed',
            type=str(EavSerializer.alias_name_to_type('kiddish')),
            uid=str(TEST_UID2),
        )

        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'base_request'],
            action='kiddish_delete',
            login=TEST_KIDDISH_LOGIN1,
            new='-',
            old='0',
            registration_datetime=TEST_REGISTRAION_DATETIME1,
            uid=str(TEST_UID2),
        )

        self.env.statbox.bind_entry(
            'subscription.passport',
            _inherit_from=['subscriptions', 'base_request'],
            operation='removed',
            sid='8',
            uid=str(TEST_UID2),
        )

        self.env.statbox.bind_entry(
            'family_kid.removed',
            _inherit_from=['family_info_modification', 'base_request'],
            attribute='uid',
            entity='kid',
            entity_id=str(TEST_UID2),
            family_id=str(TEST_FAMILY_ID),
            new='-',
            old=str(TEST_UID2),
            operation='deleted',
            uid=str(TEST_UID2),
        )

        self.setup_garbage_statbox_templates()

    def setup_garbage_statbox_templates(self):
        # Мусором в этом файле считаются те записи в лог, которые делаются не
        # смотря на то, что таких атрибутов на аккаунте нет.
        revoker_timestamp = datetime.fromtimestamp(1).strftime('%Y-%m-%d %H:%M:%S')

        attrs = {
            'account.disabled_status': 'enabled',
            'account.global_logout_datetime': revoker_timestamp,
            'account.revoker.app_passwords': revoker_timestamp,
            'account.revoker.tokens': revoker_timestamp,
            'account.revoker.web_sessions': revoker_timestamp,
        }
        for key in attrs:
            self.env.statbox.bind_entry(
                key,
                _inherit_from=['base_attr_deleted'],
                entity=key,
                old=attrs[key],
                uid=str(TEST_UID2),
            )

    def assert_ok_delete_kiddish_db(self):
        self.assertFalse(self.env.db.select('aliases', uid=TEST_UID2, db='passportdbcentral'))
        self.assertFalse(self.env.db.select('attributes', uid=TEST_UID2, db='passportdbshard1'))
        self.assertFalse(self.env.db.select('family_members', uid=TEST_UID2, db='passportdbcentral'))

    def assert_ok_delete_kiddish_event_log(self, extra_events=None):
        expected = extra_events or dict()

        e = EventCompositor(uid=str(TEST_UID2))

        req = e

        def opt(name):
            if expected.get(name):
                e(name, expected.get(name))

        req('info.login', TEST_KIDDISH_LOGIN1)
        self.garbage_events1(e)
        req('info.reg_date', '-')
        opt('info.content_rating_class')

        with e.context('family.%s.' % TEST_FAMILY_ID):
            req('family_kid', '-')

        opt('info.firstname')
        opt('info.lastname')
        req('info.display_name', '-')
        opt('info.sex')
        opt('info.birthday')
        req('info.country', '-')
        req('info.tz', '-')
        req('info.lang', '-')
        opt('info.default_avatar')
        self.garbage_events2(e)
        req('info.karma_prefix', '-')
        req('info.karma_full', '-')
        req('info.karma', '-')
        req('sid.rm', '8|' + TEST_KIDDISH_LOGIN1)
        req('action', 'kiddish_delete')
        req('consumer', TEST_CONSUMER1)
        req('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_delete_kiddish_statbox_log(self, extra_lines=None, with_check_cookies=False):
        expected = extra_lines or dict()
        entries = list()

        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies', consumer='consumer1'))

        def req(name):
            return entries.append(self.env.statbox.entry(name))

        def opt(name):
            if name in expected:
                req(name)

        self.garbage_stats1(req)
        req('account.kiddish')
        opt('account.content_rating_class')
        req('family_kid.removed')
        opt('person.firstname')
        opt('person.lastname')
        req('person.language')
        req('person.country')
        opt('person.gender')
        opt('person.birthday')
        req('person.display_name')
        opt('person.default_avatar')
        opt('person.fullname')
        req('frodo_karma')
        req('subscription.passport')

        self.env.statbox.assert_equals(entries)

    def garbage_events1(self, compositor):
        req = compositor
        req('info.ena', '-')
        req('info.disabled_status', '-')
        req('info.glogout', '-')
        req('info.tokens_revoked', '-')
        req('info.web_sessions_revoked', '-')
        req('info.app_passwords_revoked', '-')

    def garbage_events2(self, compositor):
        req = compositor
        req('info.password', '-')
        req('info.password_quality', '-')
        req('info.password_update_time', '-')
        req('info.totp', 'disabled')
        req('info.totp_update_time', '-')
        req('info.rfc_totp', 'disabled')

    def garbage_stats1(self, compositor):
        req = compositor
        req('account.global_logout_datetime')
        req('account.revoker.tokens')
        req('account.revoker.web_sessions')
        req('account.revoker.app_passwords')
        req('account.disabled_status')

    def assert_admin_blackbox_sessionid_request_ok(self, request):
        self.assertEqual(
            sorted(request.get_query_params().keys()),
            [
                'aliases',
                'attributes',
                'authid',
                'dbfields',
                'format',
                'full_info',
                'get_family_info',
                'get_login_id',
                'get_public_name',
                'guard_hosts',
                'host',
                'is_display_name_empty',
                'method',
                'multisession',
                'regname',
                'request_id',
                'sessionid',
                'sslsessionid',
                'userip',
            ],
        )
        request.assert_query_contains(
            dict(
                aliases='all_with_hidden',
                format='json',
                full_info='yes',
                get_family_info='yes',
                host=TEST_HOST,
                method='sessionid',
                multisession='yes',
                sessionid=TEST_SESSIONID_VALUE,
                userip=TEST_USER_IP1,
            ),
        )
        request.assert_contains_attributes(['account.is_disabled'])

    def assert_blackbox_family_info_request_ok(self, request):
        request.assert_query_equals(
            dict(
                family_id=TEST_FAMILY_ID,
                format='json',
                get_members_info='all',
                get_place='yes',
                method='family_info',
            ),
        )

    def assert_kiddish_blackbox_userinfo_request_ok(self, request):
        self.assertEqual(
            sorted(request.post_args.keys()),
            [
                'aliases',
                'attributes',
                'dbfields',
                'format',
                'get_family_info',
                'get_public_name',
                'is_display_name_empty',
                'method',
                'regname',
                'uid',
                'userip',
            ],
        )
        request.assert_post_data_contains(
            dict(
                aliases='all_with_hidden',
                format='json',
                get_family_info='yes',
                method='userinfo',
                uid=TEST_UID2,
                userip=TEST_USER_IP1,
            ),
        )

    def assert_admin_blackbox_userinfo_request_ok(self, request):
        self.assertEqual(
            sorted(request.post_args.keys()),
            [
                'aliases',
                'attributes',
                'dbfields',
                'format',
                'get_family_info',
                'get_public_name',
                'is_display_name_empty',
                'method',
                'regname',
                'uid',
                'userip',
            ],
        )
        request.assert_post_data_contains(
            dict(
                aliases='all_with_hidden',
                format='json',
                get_family_info='yes',
                method='userinfo',
                uid=TEST_UID,
                userip=TEST_USER_IP1,
            ),
        )
        request.assert_contains_attributes(['account.is_disabled'])


class SessionidRequestMixin(object):
    @classproperty
    def http_headers(cls):
        return merge_dicts(
            super(SessionidRequestMixin, cls).http_headers,
            {
                'cookie': TEST_USER_COOKIE,
                'host': TEST_HOST,
            }
        )


class RequiredQueryArgsMixin(object):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(RequiredQueryArgsMixin, cls).http_query_args,
            dict(
                kiddish_uid=TEST_UID2,
            ),
        )


class UserTicketRequestMixin(object):
    @classproperty
    def http_headers(cls):
        return merge_dicts(
            super(UserTicketRequestMixin, cls).http_headers,
            {
                'user_ticket': TEST_USER_TICKET1,
            },
        )


class FamilyUidRequestMixin(object):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(FamilyUidRequestMixin, cls).http_query_args,
            {
                'uid': TEST_UID,
            },
        )


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_userinfo_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('userinfo', [response])
        self._env.db.serialize(response)


class SessionidBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_sessionid_multi_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('sessionid', [response])
        self._env.db.serialize(response, 'sessionid')


class FamilyInfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        family_info_response = blackbox_family_info_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('family_info', [family_info_response])
        self._env.db.serialize(family_info_response, 'family_info')


class MinimalKiddishBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._userinfo_response = UserinfoBlackboxResponse(env)
        self._userinfo_response.kwargs.update(self.build_minimal_kiddish_kwargs())

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()

    @staticmethod
    def build_minimal_kiddish_kwargs():
        return dict(
            aliases=dict(kiddish=TEST_KIDDISH_LOGIN1),
            birthdate=None,
            city=None,
            dbfields={
                'userinfo.reg_date.uid': TEST_REGISTRAION_DATETIME1,
            },
            display_name=TEST_DISPLAY_NAME1.as_dict(),
            firstname=None,
            gender=None,
            lastname=None,
            login=TEST_KIDDISH_LOGIN1,
            uid=TEST_UID2,
        )


class FullKiddishBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._userinfo_response = UserinfoBlackboxResponse(env)
        self._userinfo_response.kwargs.update(self.build_full_kiddish_kwargs())

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()

    @staticmethod
    def build_full_kiddish_kwargs():
        kwargs = MinimalKiddishBlackboxResponse.build_minimal_kiddish_kwargs()
        attrs = kwargs.setdefault('attributes', dict())
        attrs.update(
            {
                'account.content_rating_class': str(TEST_CONTENT_RATING_CLASS1),
            },
        )

        defaults = dict(
            birthdate=TEST_BIRTHDATE1,
            default_avatar_key=TEST_DEFAULT_AVATAR1,
            firstname=TEST_FIRSTNAME1,
            gender=str(Gender.Male),
            lastname=TEST_LASTNAME1,
        )
        for key in defaults:
            if kwargs.get(key) is None:
                kwargs[key] = defaults[key]
        return kwargs


class BaseDeleteKiddishTestEnv(object):
    __metaclass__ = abc.ABCMeta

    def setup(self):
        self.setup_family_admin()
        self.setup_family_info()
        self.setup_kiddish()

    @abc.abstractmethod
    def setup_family_admin(self):
        pass

    @abc.abstractmethod
    def setup_family_info(self):
        pass

    @abc.abstractmethod
    def setup_kiddish(self):
        pass


class FamilyAdminWithKiddishTestEnv(BaseDeleteKiddishTestEnv):
    def __init__(self, env):
        self._env = env
        self.family_admin_blackbox_response = None
        self.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(env)

    def setup_family_admin(self):
        self.family_admin_blackbox_response.kwargs.update(family_info=self.build_family_info())
        self.family_admin_blackbox_response.setup()

    def setup_family_info(self):
        family_info_response = blackbox_family_info_response(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID),
            uids=[TEST_UID],
            kid_uids=[TEST_UID2],
            with_members_info=True,
        )
        self._env.blackbox.extend_response_side_effect(
            'family_info',
            [
                family_info_response,
            ],
        )
        self._env.db.serialize(family_info_response, 'family_info')

    def setup_kiddish(self):
        self.kiddish_blackbox_response.kwargs.update(family_info=self.build_family_info())
        self.kiddish_blackbox_response.setup()

    @staticmethod
    def build_family_info():
        return dict(
            admin_uid=TEST_UID,
            family_id=TEST_FAMILY_ID,
        )


class DeleteKiddishTestEnv(BaseDeleteKiddishTestEnv):
    def __init__(self, env):
        self.family_admin_blackbox_response = SessionidBlackboxResponse(env)
        self.family_info_blackbox_response = FamilyInfoBlackboxResponse(env)
        self.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(env)

    def setup_family_admin(self):
        self.family_admin_blackbox_response.setup()

    def setup_family_info(self):
        self.family_info_blackbox_response.setup()

    def setup_kiddish(self):
        self.kiddish_blackbox_response.setup()


class TestDeleteMinimalKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestDeleteMinimalKiddish, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.setup()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_ok_delete_kiddish_event_log()
        self.assert_ok_delete_kiddish_statbox_log(with_check_cookies=True)
        self.assert_admin_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_kiddish_blackbox_userinfo_request_ok(self.env.blackbox.requests[2])

    def test_no_kiddish_uid(self):
        rv = self.make_request(exclude_args=['kiddish_uid'])

        self.assert_error_response(rv, ['kiddish_uid.empty'])


class TestDeleteFullKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestDeleteFullKiddish, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = FullKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_ok_delete_kiddish_event_log(
            extra_events={
                'info.birthday': '-',
                'info.content_rating_class': '-',
                'info.default_avatar': '-',
                'info.firstname': '-',
                'info.lastname': '-',
                'info.sex': '-',
            },
        )
        self.assert_ok_delete_kiddish_statbox_log(
            extra_lines=[
                'account.content_rating_class',
                'person.birthday',
                'person.default_avatar',
                'person.firstname',
                'person.fullname',
                'person.gender',
                'person.lastname',
            ],
            with_check_cookies=True,
        )


class TestUserTicketAuthorization(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketAuthorization, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            old_setup_family_admin()

            user_ticket = fake_user_ticket(
                default_uid=TEST_UID,
                scopes=[FAMILY_MANAGE_SCOPE],
                uids=[TEST_UID],
            )
            self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

        old_setup_family_admin = tenv.setup_family_admin
        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_admin_blackbox_userinfo_request_ok(self.env.blackbox.requests[0])


class TestFamilyAdminNotDefaultInSession(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(TestFamilyAdminNotDefaultInSession, cls).http_query_args,
            dict(multisession_uid=TEST_UID),
        )

    def setUp(self):
        super(TestFamilyAdminNotDefaultInSession, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = UidNotDefaultInSessionBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()


class UidNotDefaultInSessionBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_sessionid_multi_response(uid=TEST_UID3)
        response = blackbox_sessionid_multi_append_user(response=response, **self.kwargs)
        self._env.blackbox.extend_response_side_effect('sessionid', [response])


class TestFamilyAdminNotDefaultInUserTicket(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseDeleteKiddishTestCase,
):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(TestFamilyAdminNotDefaultInUserTicket, cls).http_query_args,
            dict(multisession_uid=TEST_UID),
        )

    def setUp(self):
        super(TestFamilyAdminNotDefaultInUserTicket, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            old_setup_family_admin()

            user_ticket = fake_user_ticket(
                default_uid=TEST_UID3,
                scopes=[FAMILY_MANAGE_SCOPE],
                uids=[TEST_UID3, TEST_UID],
            )
            self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

        old_setup_family_admin = tenv.setup_family_admin
        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_admin_blackbox_userinfo_request_ok(self.env.blackbox.requests[0])


class TestAccountNotFamilyAdmin(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestAccountNotFamilyAdmin, self).setUp()

        tenv = DeleteKiddishTestEnv(self.env)
        family_info = dict(
            admin_uid=TEST_UID3,
            family_id=TEST_FAMILY_ID,
        )
        tenv.family_admin_blackbox_response.kwargs.update(family_info=family_info)
        tenv.kiddish_blackbox_response.kwargs.update(family_info=family_info)
        tenv.family_info_blackbox_response.kwargs.update(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID3),
            uids=[TEST_UID, TEST_UID3],
            kid_uids=[TEST_UID2],
            with_members_info=True,
        )
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_ok_delete_kiddish_event_log()
        self.assert_ok_delete_kiddish_statbox_log(with_check_cookies=True)
        self.assert_admin_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_kiddish_blackbox_userinfo_request_ok(self.env.blackbox.requests[2])


class TestSessionInvalid(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestSessionInvalid, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            tenv.family_admin_blackbox_response.setup()

        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.family_admin_blackbox_response.kwargs.update(status=BLACKBOX_SESSIONID_INVALID_STATUS)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])


class TestUserTicketInvalid(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketInvalid, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            old_setup_family_admin()
            self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket(uids=[TEST_UID])])

        old_setup_family_admin = tenv.setup_family_admin
        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.invalid'])


class TestUserTicketScopeInvalid(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketScopeInvalid, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            old_setup_family_admin()

            user_ticket = fake_user_ticket(
                default_uid=TEST_UID,
                scopes=['invalid'],
                uids=[TEST_UID],
            )
            self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

        old_setup_family_admin = tenv.setup_family_admin
        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.missing_scopes'])


class TestAccountWithoutFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestAccountWithoutFamily, self).setUp()

        tenv = DeleteKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response.kwargs.update(family_info=None)
        tenv.family_info_blackbox_response.kwargs.update(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID3),
            uids=[TEST_UID3],
            kid_uids=[TEST_UID2],
            with_members_info=True,
        )
        tenv.kiddish_blackbox_response.kwargs.update(
            family_info=dict(
                admin_uid=TEST_UID3,
                family_id=TEST_FAMILY_ID,
            ),
        )
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.does_not_exist'])


class TestNeighbourKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    """
    Удаление чужого (соседского) ребёнкиша
    """
    def setUp(self):
        super(TestNeighbourKiddish, self).setUp()

        tenv = DeleteKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response.kwargs.update(
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID,
            ),
        )
        tenv.family_info_blackbox_response.kwargs.update(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID),
            uids=[TEST_UID],
            kid_uids=[TEST_UID3],
            with_members_info=True,
        )
        tenv.kiddish_blackbox_response.kwargs.update(
            family_info=dict(
                admin_uid=TEST_UID4,
                family_id=TEST_FAMILY_ID1,
            ),
        )
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.is_not_a_member'])


class TestKiddishDisabled(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestKiddishDisabled, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response.kwargs.update(enabled=False)
        tenv.setup()

    def setup_statbox_templates(self):
        super(TestKiddishDisabled, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'account.disabled_status',
            _inherit_from=['account.disabled_status'],
            old='disabled',
        )

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_ok_delete_kiddish_event_log()
        self.assert_ok_delete_kiddish_statbox_log(with_check_cookies=True)


class TestRaceKiddishNotKiddishInSameFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и оставили в той же семье
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishInSameFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response.kwargs.update(
            aliases=dict(
                kiddish=TEST_KIDDISH_LOGIN1,
                portal=TEST_LOGIN1,
            ),
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID,
            ),
            login=TEST_LOGIN1,
            uid=TEST_UID2,
        )

        def new_setup_kiddish():
            tenv.kiddish_blackbox_response.setup()

        tenv.setup_kiddish = new_setup_kiddish
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['internal.temporary'])


class TestRaceKiddishNotKiddishWithoutFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и оставили без семьи
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishWithoutFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response.kwargs.update(
            aliases=dict(
                kiddish=TEST_KIDDISH_LOGIN1,
                portal=TEST_LOGIN1,
            ),
            family_info=None,
            login=TEST_LOGIN1,
            uid=TEST_UID2,
        )

        def new_setup_kiddish():
            tenv.kiddish_blackbox_response.setup()

        tenv.setup_kiddish = new_setup_kiddish
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.is_not_a_member'])


class TestRaceKiddishNotKiddishMoveToOtherFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и он вступил в другую
    семью.
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishMoveToOtherFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response.kwargs.update(
            aliases=dict(
                kiddish=TEST_KIDDISH_LOGIN1,
                portal=TEST_LOGIN1,
            ),
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID1,
            ),
            login=TEST_LOGIN1,
            uid=TEST_UID2,
        )

        def new_setup_kiddish():
            tenv.kiddish_blackbox_response.setup()

        tenv.setup_kiddish = new_setup_kiddish
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.is_not_a_member'])


class TestUserTicketWithSessionidScope(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketWithSessionidScope, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            old_setup_family_admin()

            user_ticket = fake_user_ticket(
                default_uid=TEST_UID,
                scopes=[SESSIONID_SCOPE],
                uids=[TEST_UID],
            )
            self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

        old_setup_family_admin = tenv.setup_family_admin
        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv)


class TestByUid(
    RequiredQueryArgsMixin,
    FamilyUidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestByUid, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.setup()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_delete_kiddish_db()
        self.assert_ok_delete_kiddish_event_log()
        self.assert_ok_delete_kiddish_statbox_log()

    def test_no_uid(self):
        rv = self.make_request(exclude_args=['uid'])

        self.assert_error_response(rv, ['request.credentials_all_missing'])


class TestAccountKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseDeleteKiddishTestCase,
):
    def setUp(self):
        super(TestAccountKiddish, self).setUp()

        tenv = DeleteKiddishTestEnv(self.env)
        family_info = dict(
            admin_uid=TEST_UID3,
            family_id=TEST_FAMILY_ID,
        )
        tenv.family_admin_blackbox_response.kwargs.update(
            aliases=dict(kiddish=TEST_KIDDISH_LOGIN2),
            family_info=family_info,
        )
        tenv.kiddish_blackbox_response.kwargs.update(family_info=family_info)
        tenv.family_info_blackbox_response.kwargs.update(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID3),
            uids=[TEST_UID3],
            kid_uids=[TEST_UID, TEST_UID2],
            with_members_info=True,
        )
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.not_allowed_to_manage_kiddish'])
