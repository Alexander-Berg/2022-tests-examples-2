# -*- coding: utf-8 -*-

import abc

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
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.consts import (
    TEST_BIRTHDATE1,
    TEST_BIRTHDATE2,
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_DEFAULT_AVATAR1,
    TEST_DEFAULT_AVATAR2,
    TEST_FIRSTNAME1,
    TEST_FIRSTNAME2,
    TEST_KIDDISH_LOGIN1,
    TEST_KIDDISH_LOGIN2,
    TEST_LASTNAME1,
    TEST_LASTNAME2,
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
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.string import smart_text


TEST_CONTENT_RATING_CLASS1 = 2
TEST_CONTENT_RATING_CLASS2 = 1
TEST_CONTENT_RATING_CLASS3 = 3
TEST_DISPLAY_NAME1 = DisplayName(u'Попосерик2020')
TEST_DISPLAY_NAME2 = DisplayName(u'Попосерик2021')


@with_settings_hosts()
class BaseChangeKiddishTestCase(BaseFamilyTestcase):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/family/change_kiddish/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_agent': TEST_USER_AGENT1,
        'user_ip': TEST_USER_IP1,
    }
    http_method = 'POST'

    def setUp(self):
        super(BaseChangeKiddishTestCase, self).setUp()

        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    grants={
                        'family': [
                            'change_kiddish',
                            'change_kiddish_by_uid',
                        ],
                    },
                    networks=[TEST_CONSUMER_IP1],
                ),
            },
        )

    def build_ok_change_kiddish_response(
        self,
        content_rating_class=None,
        birthday=None,
        default_avatar=None,
        firstname=None,
        gender=None,
        lastname=None,
        music_content_rating_class=None,
        video_content_rating_class=None,
    ):
        if default_avatar is None:
            default_avatar = ''

        display_name_response = dict(
            default_avatar=default_avatar,
            name=TEST_DISPLAY_NAME1.name,
        )

        person_response = dict(
            country='ru',
            firstname=firstname,
            language='ru',
            lastname=lastname,
        )
        if birthday is not None:
            person_response.update(birthday=birthday)
        if gender is not None:
            person_response.update(gender=gender)

        account_response = dict(
            display_login='',
            display_name=display_name_response,
            login=TEST_KIDDISH_LOGIN1,
            person=person_response,
            place_id='%s:100' % TEST_FAMILY_ID,
            uid=TEST_UID2,
        )
        if content_rating_class is not None:
            account_response.update(content_rating_class=content_rating_class)
        if music_content_rating_class is not None:
            account_response.update(music_content_rating_class=music_content_rating_class)
        if video_content_rating_class is not None:
            account_response.update(video_content_rating_class=video_content_rating_class)

        return dict(account=account_response)

    def build_ok_change_kiddish_full_response(self, display_name=Undefined, **kwargs):
        defaults = dict(
            birthday=TEST_BIRTHDATE1,
            content_rating_class=TEST_CONTENT_RATING_CLASS1,
            default_avatar=TEST_DEFAULT_AVATAR1,
            firstname=TEST_FIRSTNAME1,
            gender=Gender.Male,
            lastname=TEST_LASTNAME1,
            music_content_rating_class=TEST_CONTENT_RATING_CLASS2,
            video_content_rating_class=TEST_CONTENT_RATING_CLASS3,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        response = self.build_ok_change_kiddish_response(**kwargs)

        if display_name is not Undefined:
            display_name_response = display_name.as_dict()
            response = deep_merge(response, dict(account=dict(display_name=display_name_response)))

        return response

    def setup_statbox_templates(self):
        super(BaseChangeKiddishTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'base_request',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT1,
        )

        self.env.statbox.bind_entry(
            'base_attr_created',
            _inherit_from=['account_modification', 'base_request'],
            new='-',
            old='-',
            operation='created',
        )

        self.env.statbox.bind_entry(
            'base_attr_updated',
            _inherit_from=['account_modification', 'base_request'],
            new='-',
            old='-',
            operation='updated',
        )

        self.env.statbox.bind_entry(
            'base_attr_deleted',
            _inherit_from=['account_modification', 'base_request'],
            new='-',
            old='-',
            operation='deleted',
        )

    def assert_attr_changed_event_log(self, attr_name, attr_value):
        e = EventCompositor(uid=str(TEST_UID2))
        e(attr_name, attr_value)
        e('action', 'kiddish_change')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)
        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

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


class RequiredQueryArgsMixin(object):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(RequiredQueryArgsMixin, cls).http_query_args,
            dict(
                kiddish_uid=TEST_UID2,
            ),
        )


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


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


class BaseChangeKiddishTestEnv(object):
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


class FamilyAdminWithKiddishTestEnv(BaseChangeKiddishTestEnv):
    def __init__(self, env):
        self._env = env
        self.family_admin_blackbox_response = None
        self.kiddish_blackbox_response = None

    def setup_family_admin(self):
        self.family_admin_blackbox_response.kwargs.update(family_info=self.build_family_info())
        self.family_admin_blackbox_response.setup()

    def setup_family_info(self):
        response = FamilyInfoBlackboxResponse(self._env)
        response.kwargs.update(
            family_id=TEST_FAMILY_ID,
            admin_uid=str(TEST_UID),
            uids=[TEST_UID],
            kid_uids=[TEST_UID2],
            with_members_info=True,
        )
        response.setup()

    def setup_kiddish(self):
        self.kiddish_blackbox_response.kwargs.update(family_info=self.build_family_info())
        self.kiddish_blackbox_response.setup()

    @staticmethod
    def build_family_info():
        return dict(
            admin_uid=TEST_UID,
            family_id=TEST_FAMILY_ID,
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
                'account.music_content_rating_class': str(TEST_CONTENT_RATING_CLASS2),
                'account.video_content_rating_class': str(TEST_CONTENT_RATING_CLASS3),
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


class TestCreateAttr(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestCreateAttr, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_avatar_id(self):
        rv = self.make_request(query_args=dict(avatar_id=TEST_DEFAULT_AVATAR1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(default_avatar=TEST_DEFAULT_AVATAR1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'avatar.default', TEST_DEFAULT_AVATAR1)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.default_avatar',
                    new=TEST_DEFAULT_AVATAR1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.default_avatar', TEST_DEFAULT_AVATAR1)

    def test_birthday(self):
        rv = self.make_request(query_args=dict(birthday=TEST_BIRTHDATE1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(birthday=TEST_BIRTHDATE1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.birthday', TEST_BIRTHDATE1)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.birthday',
                    new=TEST_BIRTHDATE1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.birthday', TEST_BIRTHDATE1)

    def test_content_rating_class(self):
        rv = self.make_request(query_args=dict(content_rating_class=TEST_CONTENT_RATING_CLASS1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(
                content_rating_class=TEST_CONTENT_RATING_CLASS1,
                music_content_rating_class=TEST_CONTENT_RATING_CLASS1,
                video_content_rating_class=TEST_CONTENT_RATING_CLASS1,
            )
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.content_rating_class', str(TEST_CONTENT_RATING_CLASS1))
        self.env.db.check_db_attr_missing(TEST_UID2, 'account.music_content_rating_class')
        self.env.db.check_db_attr_missing(TEST_UID2, 'account.video_content_rating_class')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='account.content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.content_rating_class', str(TEST_CONTENT_RATING_CLASS1))

    def test_firstname(self):
        rv = self.make_request(query_args={'firstname': TEST_FIRSTNAME1})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(firstname=TEST_FIRSTNAME1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.firstname', TEST_FIRSTNAME1.encode('utf8'))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.firstname',
                    new=TEST_FIRSTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.fullname',
                    new=TEST_FIRSTNAME1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.firstname', TEST_FIRSTNAME1.encode('utf8'))

    def test_gender(self):
        rv = self.make_request(query_args=dict(gender=Gender.to_char(Gender.Male)))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(gender=Gender.Male)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.gender', Gender.to_char(Gender.Male))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.gender',
                    new=Gender.to_char(Gender.Male),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.sex', str(Gender.Male))

    def test_lastname(self):
        rv = self.make_request(query_args=dict(lastname=TEST_LASTNAME1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(lastname=TEST_LASTNAME1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.lastname', TEST_LASTNAME1.encode('utf8'))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.lastname',
                    new=TEST_LASTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='person.fullname',
                    new=TEST_LASTNAME1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.lastname', TEST_LASTNAME1.encode('utf8'))

    def test_music_content_rating_class(self):
        rv = self.make_request(query_args=dict(music_content_rating_class=TEST_CONTENT_RATING_CLASS2))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(music_content_rating_class=TEST_CONTENT_RATING_CLASS2)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='account.music_content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS2),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

    def test_video_content_rating_class(self):
        rv = self.make_request(query_args=dict(video_content_rating_class=TEST_CONTENT_RATING_CLASS3))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(video_content_rating_class=TEST_CONTENT_RATING_CLASS3)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.video_content_rating_class', str(TEST_CONTENT_RATING_CLASS3))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_created',
                    entity='account.video_content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS3),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.video_content_rating_class', str(TEST_CONTENT_RATING_CLASS3))


class TestChangeAttr(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestChangeAttr, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = FullKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_avatar_id(self):
        rv = self.make_request(query_args=dict(avatar_id=TEST_DEFAULT_AVATAR2))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(default_avatar=TEST_DEFAULT_AVATAR2)
        )

        self.env.db.check_db_attr(TEST_UID2, 'avatar.default', TEST_DEFAULT_AVATAR2)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.default_avatar',
                    new=TEST_DEFAULT_AVATAR2,
                    old=TEST_DEFAULT_AVATAR1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.default_avatar', TEST_DEFAULT_AVATAR2)

    def test_birthday(self):
        rv = self.make_request(query_args=dict(birthday=TEST_BIRTHDATE2))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(birthday=TEST_BIRTHDATE2)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.birthday', TEST_BIRTHDATE2)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.birthday',
                    new=TEST_BIRTHDATE2,
                    old=TEST_BIRTHDATE1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.birthday', TEST_BIRTHDATE2)

    def test_content_rating_class(self):
        rv = self.make_request(query_args=dict(content_rating_class=TEST_CONTENT_RATING_CLASS2))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(content_rating_class=TEST_CONTENT_RATING_CLASS2)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='account.content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS2),
                    old=str(TEST_CONTENT_RATING_CLASS1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

    def test_content_rating_class_to_zero(self):
        rv = self.make_request(query_args=dict(content_rating_class='0'))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(content_rating_class=0)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.content_rating_class', '0')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='account.content_rating_class',
                    new='0',
                    old=str(TEST_CONTENT_RATING_CLASS1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.content_rating_class', '0')

    def test_display_name(self):
        rv = self.make_request(query_args={'display_name': TEST_DISPLAY_NAME2.name})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(display_name=TEST_DISPLAY_NAME2)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.display_name', str(TEST_DISPLAY_NAME2))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.display_name',
                    new=TEST_DISPLAY_NAME2,
                    old=TEST_DISPLAY_NAME1,
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.display_name', str(TEST_DISPLAY_NAME2))

    def test_firstname(self):
        rv = self.make_request(query_args={'firstname': TEST_FIRSTNAME2})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(
                firstname=TEST_FIRSTNAME2,
            )
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.firstname', TEST_FIRSTNAME2.encode('utf8'))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.firstname',
                    new=TEST_FIRSTNAME2,
                    old=TEST_FIRSTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.fullname',
                    new=u'%s %s' % (TEST_FIRSTNAME2, TEST_LASTNAME1),
                    old=u'%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.firstname', TEST_FIRSTNAME2.encode('utf8'))

    def test_gender(self):
        rv = self.make_request(query_args=dict(gender=Gender.to_char(Gender.Female)))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(gender=Gender.Female)
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.gender', Gender.to_char(Gender.Female))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.gender',
                    new=Gender.to_char(Gender.Female),
                    old=Gender.to_char(Gender.Male),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.sex', str(Gender.Female))

    def test_lastname(self):
        rv = self.make_request(query_args={'lastname': TEST_LASTNAME2})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(
                lastname=TEST_LASTNAME2,
            )
        )

        self.env.db.check_db_attr(TEST_UID2, 'person.lastname', TEST_LASTNAME2.encode('utf8'))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.lastname',
                    new=TEST_LASTNAME2,
                    old=TEST_LASTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.fullname',
                    new=u'%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME2),
                    old=u'%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.lastname', TEST_LASTNAME2.encode('utf8'))

    def test_music_content_rating_class(self):
        rv = self.make_request(query_args=dict(music_content_rating_class=TEST_CONTENT_RATING_CLASS1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(music_content_rating_class=TEST_CONTENT_RATING_CLASS1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS1))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='account.music_content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS1),
                    old=str(TEST_CONTENT_RATING_CLASS2),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS1))

    def test_video_content_rating_class(self):
        rv = self.make_request(query_args=dict(video_content_rating_class=TEST_CONTENT_RATING_CLASS1))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(video_content_rating_class=TEST_CONTENT_RATING_CLASS1)
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.video_content_rating_class', str(TEST_CONTENT_RATING_CLASS1))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='account.video_content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS1),
                    old=str(TEST_CONTENT_RATING_CLASS3),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.video_content_rating_class', str(TEST_CONTENT_RATING_CLASS1))


class TestDeleteAttr(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestDeleteAttr, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = FullKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_avatar_id(self):
        rv = self.make_request(query_args={'avatar_id': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(default_avatar='')
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'avatar.default')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='person.default_avatar',
                    old=smart_text(TEST_DEFAULT_AVATAR1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.default_avatar', '-')

    def test_birthday(self):
        rv = self.make_request(query_args={'birthday': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(birthday=None)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'person.birthday')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='person.birthday',
                    old=smart_text(TEST_BIRTHDATE1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.birthday', '-')

    def test_content_rating_class(self):
        rv = self.make_request(query_args={'content_rating_class': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(content_rating_class=None)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'account.content_rating_class')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='account.content_rating_class',
                    old=str(TEST_CONTENT_RATING_CLASS1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.content_rating_class', '-')

    def test_display_name(self):
        rv = self.make_request(query_args={'display_name': ''})

        self.assert_error_response(rv, ['display_name.empty'])

    def test_firstname(self):
        rv = self.make_request(query_args={'firstname': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(
                firstname=None,
            )
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'person.firstname')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='person.firstname',
                    old=TEST_FIRSTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.fullname',
                    new=TEST_LASTNAME1,
                    old=u'%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.firstname', '-')

    def test_gender(self):
        rv = self.make_request(query_args={'gender': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(gender=None)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'person.gender')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='person.gender',
                    old=Gender.to_char(Gender.Male),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.sex', '-')

    def test_lastname(self):
        rv = self.make_request(query_args={'lastname': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(
                lastname=None,
            )
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'person.lastname')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='person.lastname',
                    old=TEST_LASTNAME1,
                    uid=str(TEST_UID2),
                ),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='person.fullname',
                    new=TEST_FIRSTNAME1,
                    old=u'%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.lastname', '-')

    def test_music_content_rating_class(self):
        rv = self.make_request(query_args={'music_content_rating_class': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(music_content_rating_class=TEST_CONTENT_RATING_CLASS1)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'account.music_content_rating_class')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='account.music_content_rating_class',
                    old=str(TEST_CONTENT_RATING_CLASS2),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.music_content_rating_class', '-')

    def test_video_content_rating_class(self):
        rv = self.make_request(query_args={'video_content_rating_class': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_full_response(video_content_rating_class=TEST_CONTENT_RATING_CLASS1)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'account.video_content_rating_class')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='account.video_content_rating_class',
                    old=str(TEST_CONTENT_RATING_CLASS3),
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.video_content_rating_class', '-')


class TestSessionidAuthorization(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestSessionidAuthorization, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())

        self.assert_admin_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_kiddish_blackbox_userinfo_request_ok(self.env.blackbox.requests[2])

    def test_no_kiddish_uid(self):
        rv = self.make_request(exclude_args=['kiddish_uid'])

        self.assert_error_response(rv, ['kiddish_uid.empty'])


class TestUserTicketAuthorization(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseChangeKiddishTestCase,
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
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())
        self.assert_admin_blackbox_userinfo_request_ok(self.env.blackbox.requests[0])


class TestFamilyAdminNotDefaultInSession(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
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
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()
        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())


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
    BaseChangeKiddishTestCase,
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
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())
        self.assert_admin_blackbox_userinfo_request_ok(self.env.blackbox.requests[0])


class TestAccountNotFamilyAdmin(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestAccountNotFamilyAdmin, self).setUp()

        tenv = ChangeKiddishTestEnv(self.env)
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

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())

        self.assert_admin_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_kiddish_blackbox_userinfo_request_ok(self.env.blackbox.requests[2])


class TestSessionInvalid(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestSessionInvalid, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)

        def new_setup_family_admin():
            tenv.family_admin_blackbox_response.setup()

        tenv.setup_family_admin = new_setup_family_admin

        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.family_admin_blackbox_response.kwargs.update(status=BLACKBOX_SESSIONID_INVALID_STATUS)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])


class TestUserTicketInvalid(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseChangeKiddishTestCase,
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
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.invalid'])


class TestUserTicketScopeInvalid(
    RequiredQueryArgsMixin,
    UserTicketRequestMixin,
    BaseChangeKiddishTestCase,
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
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.missing_scopes'])


class ChangeKiddishTestEnv(BaseChangeKiddishTestEnv):
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


class TestAccountWithoutFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestAccountWithoutFamily, self).setUp()

        tenv = ChangeKiddishTestEnv(self.env)
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


class TestAccountKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestAccountKiddish, self).setUp()

        tenv = ChangeKiddishTestEnv(self.env)
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


class TestNeighbourKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    """
    Удаление чужого (соседского) ребёнкиша
    """
    def setUp(self):
        super(TestNeighbourKiddish, self).setUp()

        tenv = ChangeKiddishTestEnv(self.env)
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
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestKiddishDisabled, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response.kwargs.update(enabled=False)
        tenv.setup()

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())


class TestRaceKiddishNotKiddishInSameFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и оставили в той же семье
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishInSameFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
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
    BaseChangeKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и оставили без семьи
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishWithoutFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
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
    BaseChangeKiddishTestCase,
):
    """
    За время вызова ручки ребёнкиша дорегистрировали и он вступил в другую
    семью.
    """
    def setUp(self):
        super(TestRaceKiddishNotKiddishMoveToOtherFamily, self).setUp()

        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
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
    BaseChangeKiddishTestCase,
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

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())


class TestByUid(
    RequiredQueryArgsMixin,
    FamilyUidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestByUid, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = UserinfoBlackboxResponse(self.env)
        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        tenv.setup()

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_change_kiddish_response())

    def test_no_uid(self):
        rv = self.make_request(exclude_args=['uid'])

        self.assert_error_response(rv, ['request.credentials_all_missing'])


class TestZeroContentRatingClassAttr(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseChangeKiddishTestCase,
):
    def setUp(self):
        super(TestZeroContentRatingClassAttr, self).setUp()
        tenv = FamilyAdminWithKiddishTestEnv(self.env)
        tenv.family_admin_blackbox_response = SessionidBlackboxResponse(self.env)

        tenv.kiddish_blackbox_response = MinimalKiddishBlackboxResponse(self.env)
        attrs = tenv.kiddish_blackbox_response.kwargs.setdefault('attributes', dict())
        attrs.update({'account.music_content_rating_class': '0'})

        tenv.setup()

    def test_change(self):
        rv = self.make_request(query_args=dict(music_content_rating_class=TEST_CONTENT_RATING_CLASS2))

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(
                music_content_rating_class=TEST_CONTENT_RATING_CLASS2,
            )
        )

        self.env.db.check_db_attr(TEST_UID2, 'account.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_updated',
                    entity='account.music_content_rating_class',
                    new=str(TEST_CONTENT_RATING_CLASS2),
                    old='0',
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.music_content_rating_class', str(TEST_CONTENT_RATING_CLASS2))

    def test_delete(self):
        rv = self.make_request(query_args={'music_content_rating_class': ''})

        self.assert_ok_response(
            rv,
            **self.build_ok_change_kiddish_response(music_content_rating_class=None)
        )

        self.env.db.check_db_attr_missing(TEST_UID2, 'account.music_content_rating_class')

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_cookies', consumer='consumer1'),
                self.env.statbox.entry(
                    'base_attr_deleted',
                    entity='account.music_content_rating_class',
                    old='0',
                    uid=str(TEST_UID2),
                ),
            ],
        )

        self.assert_attr_changed_event_log('info.music_content_rating_class', '-')
