# -*- coding: utf-8 -*-

import functools
import itertools

import mock
from nose_parameterized import parameterized
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
    blackbox_loginoccupation_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE,
    get_attr_name,
)
from passport.backend.core.models.family import FamilyMember
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.test.consts import (
    TEST_BIRTHDATE1,
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_DEFAULT_AVATAR1,
    TEST_FIRSTNAME1,
    TEST_KIDDISH_LOGIN1,
    TEST_LASTNAME1,
    TEST_PHONE_NUMBER1,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
    TEST_USER_TICKET1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
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
TEST_CONTENT_RATING_CLASS2 = 3
TEST_CONTENT_RATING_CLASS3 = 4
TEST_DISPLAY_NAME1 = DisplayName(u'Попосерик2020')


def all_special_content_types():
    all_types = list()
    for attr_name in ATTRIBUTE_NAME_TO_TYPE:
        if (
            attr_name != 'account.content_rating_class' and
            attr_name.startswith('account.') and
            attr_name.endswith('_content_rating_class')
        ):
            content_type = attr_name[len('account.'):][:-len('_content_rating_class')]
            all_types.append(content_type)
    return all_types


@with_settings_hosts(
    FAMILY_MAX_KIDS_NUMBER=1,
    FAMILY_MAX_SIZE=1,
)
class BaseCreateKiddishTestCase(BaseFamilyTestcase):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/family/create_kiddish/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_agent': TEST_USER_AGENT1,
        'user_ip': TEST_USER_IP1,
    }
    http_method = 'POST'

    def setUp(self):
        super(BaseCreateKiddishTestCase, self).setUp()

        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    grants={
                        'family': [
                            'create_kiddish',
                            'create_kiddish_by_family_id',
                        ],
                    },
                    networks=[TEST_CONSUMER_IP1],
                ),
            },
        )

        self.setup_new_kiddish_uid()

        self.env.blackbox.set_response_side_effect(
            'loginoccupation',
            [
                blackbox_loginoccupation_response({TEST_KIDDISH_LOGIN1: 'free'}),
            ],
        )

        self.env.login_generator.set_response_value('kiddish', TEST_KIDDISH_LOGIN1)

    def setup_new_kiddish_uid(self):
        self.env.db.set_side_effect_for_db(
            'passportdbcentral',
            itertools.chain(
                [mock.Mock(inserted_primary_key=[TEST_UID2])],
                itertools.repeat(mock.DEFAULT),
            ),
        )

    def assert_ok_create_kiddish_db(
        self,
        extra_attrs=None,
        extra_family_members=None,
    ):
        """
        Входные параметры

            extra_attrs

                Словарь (имя атрибута, значение) с атрибутами, которые должны
                быть у ребёнкиша, помимо обязательных.

            extra_family_members

                Список объектов FamilyMember соответсвующих участникам, которые
                должны быть в семье, помимо обязательных.
        """

        self.env.db.check('aliases', 'kiddish', TEST_KIDDISH_LOGIN1, uid=TEST_UID2, db='passportdbcentral')

        aliases = self.env.db.select('aliases', uid=TEST_UID2, db='passportdbcentral')
        self.assertEqual(len(aliases), 1)

        expected_attrs = dict()
        if extra_attrs:
            expected_attrs.update(extra_attrs)
        for key in self.kiddish_required_attributes:
            if key not in expected_attrs:
                expected_attrs[key] = self.kiddish_required_attributes[key]

        attrs = self.env.db.select('attributes', uid=TEST_UID2, db='passportdbshard1')
        attrs = {get_attr_name(a['type']): a['value'] for a in attrs}
        self.assertEqual(attrs, expected_attrs)

        self.assertFalse(self.env.db.select('extended_attributes', uid=TEST_UID2, db='passportdbshard1'))

        expected_family_members = self.expected_family_members
        if extra_family_members:
            expected_family_members = deep_merge(expected_family_members, extra_family_members)

        family_id = int(TEST_FAMILY_ID[1:])
        expected_family_members = [dict(family_id=family_id, place=m.place, uid=m.uid) for m in expected_family_members]
        self.env.db.check_table_contents(
            table_name='family_members',
            db_name='passportdbcentral',
            expected=expected_family_members,
        )

    @property
    def kiddish_required_attributes(self):
        """
        Параметры, которые должны быть обязательно заполнены непустыми значениями
        """
        return {
            'account.display_name': str(TEST_DISPLAY_NAME1),
            'account.registration_datetime': TimeNow(),
            'person.timezone': mock.ANY,
        }

    @property
    def expected_family_members(self):
        return [
            FamilyMember(uid=TEST_UID, place=0),
            FamilyMember(uid=TEST_UID2, place=self.expected_kiddish_place),
        ]

    expected_kiddish_place = 100

    def assert_ok_create_kiddish_event_log(self, extra_events=None):
        expected = extra_events or dict()
        required_events = {'info.login': TEST_KIDDISH_LOGIN1}
        for name in required_events:
            if name not in expected:
                expected[name] = required_events[name]

        e = EventCompositor(uid=str(TEST_UID2))

        def opt(name):
            if name in expected:
                e(name, expected[name])

        e('info.login', expected['info.login'])
        e('info.ena', '1')
        e('info.disabled_status', '0')
        e('info.reg_date', DatetimeNow(convert_to_datetime=True))
        opt('info.content_rating_class')
        opt('info.music_content_rating_class')
        opt('info.video_content_rating_class')
        opt('info.firstname')
        opt('info.lastname')
        e('info.display_name', str(TEST_DISPLAY_NAME1))
        opt('info.sex')
        opt('info.birthday')
        e('info.country', mock.ANY)
        e('info.tz', mock.ANY)
        e('info.lang', mock.ANY)
        opt('info.default_avatar')
        e('info.karma_prefix', '0')
        e('info.karma_full', '0')
        e('info.karma', '0')
        e('alias.kiddish.add', TEST_KIDDISH_LOGIN1)
        e('sid.add', '8|' + TEST_KIDDISH_LOGIN1)
        e('action', 'kiddish_create')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        with e.context('family.%s.' % TEST_FAMILY_ID):
            e('family_kid', str(TEST_UID2))
        e('action', 'family_add_kiddish')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_create_kiddish_statbox_log(self, extra_lines=None):
        expected = extra_lines or dict()
        lines = list()
        lines.append(self.env.statbox.entry('check_cookies', consumer='consumer1'))

        def req(name):
            lines.append(self.env.statbox.entry(name))

        def opt(name):
            if name in expected:
                lines.append(self.env.statbox.entry(name))

        req('account.disabled_status')
        req('aliases.kiddish')
        opt('account.content_rating_class')
        opt('account.music_content_rating_class')
        opt('account.video_content_rating_class')
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
        req('family_kid.added')

        self.env.statbox.assert_equals(lines)

    def setup_statbox_templates(self):
        super(BaseCreateKiddishTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'base_request',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'base_attr_created',
            _inherit_from=['account_modification', 'base_request'],
            entity='-',
            new='-',
            old='-',
            operation='created',
        )

        self.env.statbox.bind_entry(
            'aliases.kiddish',
            _inherit_from=['account_modification', 'base_request'],
            entity='aliases',
            operation='added',
            type=str(EavSerializer.alias_name_to_type('kiddish')),
            value=TEST_KIDDISH_LOGIN1,
            uid=str(TEST_UID2),
        )

        attrs = {
            'account.content_rating_class': str(TEST_CONTENT_RATING_CLASS1),
            'account.music_content_rating_class': str(TEST_CONTENT_RATING_CLASS2),
            'account.video_content_rating_class': str(TEST_CONTENT_RATING_CLASS3),
            'account.disabled_status': 'enabled',
            'person.firstname': smart_text(TEST_FIRSTNAME1),
            'person.lastname': smart_text(TEST_LASTNAME1),
            'person.language': mock.ANY,
            'person.country': mock.ANY,
            'person.gender': Gender.to_char(Gender.Male),
            'person.birthday': TEST_BIRTHDATE1,
            'person.display_name': smart_text(TEST_DISPLAY_NAME1),
            'person.default_avatar': TEST_DEFAULT_AVATAR1,
            'person.fullname': smart_text('%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1)),
        }
        for key in attrs:
            self.env.statbox.bind_entry(
                key,
                _inherit_from=['base_attr_created'],
                entity=key,
                new=attrs[key],
                uid=str(TEST_UID2),
            )

        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'base_request'],
            action='kiddish_create',
            login=TEST_KIDDISH_LOGIN1,
            registration_datetime=functools.partial(DatetimeNow, convert_to_datetime=True),
            uid=str(TEST_UID2),
        )
        self.env.statbox.bind_entry(
            'subscription.passport',
            _inherit_from=['subscriptions', 'base_request'],
            operation='added',
            sid='8',
            uid=str(TEST_UID2),
        )
        self.env.statbox.bind_entry(
            'family_kid.added',
            _inherit_from=['family_info_modification', 'base_request'],
            attribute='uid',
            entity='kid',
            entity_id=str(TEST_UID2),
            family_id=str(TEST_FAMILY_ID),
            new=str(TEST_UID2),
            old='-',
            operation='created',
        )

    def build_create_kiddish_response(self):
        display_name_response = dict(
            default_avatar='',
            name=TEST_DISPLAY_NAME1.name,
        )
        person_response = dict(
            country='ru',
            firstname=None,
            language='ru',
            lastname=None,
        )
        account_response = dict(
            display_login='',
            display_name=display_name_response,
            login=TEST_KIDDISH_LOGIN1,
            person=person_response,
            place_id='%s:%s' % (TEST_FAMILY_ID, self.expected_kiddish_place),
            uid=TEST_UID2,
        )
        return dict(account=account_response)

    def assert_blackbox_sessionid_request_ok(self, request):
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

    def assert_blackbox_userinfo_request_ok(self, request):
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

    def assert_blackbox_loginoccupation_request_ok(self, request):
        request.assert_query_equals(
            dict(
                format='json',
                ignore_stoplist='1',
                logins=TEST_KIDDISH_LOGIN1,
                method='loginoccupation',
            ),
        )


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
            }
        )


class RequiredQueryArgsMixin(object):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(RequiredQueryArgsMixin, cls).http_query_args,
            dict(
                display_name=TEST_DISPLAY_NAME1.name,
            ),
        )


class AdminWithoutKidsTestCase(BaseCreateKiddishTestCase):
    def setUp(self):
        super(AdminWithoutKidsTestCase, self).setUp()

        self._family_to_db(
            family_id=TEST_FAMILY_ID,
            admin_uid=TEST_UID,
            uids=[TEST_UID],
        )

        authorization_kwargs = dict(
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID,
            ),
        )

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(**authorization_kwargs),
            ],
        )

        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**authorization_kwargs),
            ],
        )

        user_ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=[FAMILY_MANAGE_SCOPE],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

        self.env.blackbox.set_blackbox_response_side_effect(
            'family_info',
            [
                blackbox_family_info_response(
                    family_id=TEST_FAMILY_ID,
                    admin_uid=str(TEST_UID),
                    uids=[TEST_UID],
                    with_members_info=True,
                ),
            ]
        )


class TestAdminWithoutKids(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    AdminWithoutKidsTestCase,
):
    def test_required_and_optional_args(self):
        rv = self.make_request(
            query_args=dict(
                avatar_id=TEST_DEFAULT_AVATAR1,
                birthday=TEST_BIRTHDATE1,
                content_rating_class=str(TEST_CONTENT_RATING_CLASS1),
                family_id=TEST_FAMILY_ID,
                firstname=TEST_FIRSTNAME1,
                gender=Gender.to_char(Gender.Male),
                lastname=TEST_LASTNAME1,
                music_content_rating_class=str(TEST_CONTENT_RATING_CLASS2),
                uid=str(TEST_UID),
                video_content_rating_class=str(TEST_CONTENT_RATING_CLASS3),
            ),
        )

        expected_response = deep_merge(
            self.build_create_kiddish_response(),
            dict(
                account=dict(
                    content_rating_class=TEST_CONTENT_RATING_CLASS1,
                    music_content_rating_class=TEST_CONTENT_RATING_CLASS2,
                    video_content_rating_class=TEST_CONTENT_RATING_CLASS3,
                    display_name=dict(
                        default_avatar=TEST_DEFAULT_AVATAR1,
                    ),
                    person=dict(
                        birthday=TEST_BIRTHDATE1,
                        firstname=smart_text(TEST_FIRSTNAME1),
                        gender=Gender.Male,
                        lastname=smart_text(TEST_LASTNAME1),
                    ),
                ),
            ),
        )
        self.assert_ok_response(rv, **expected_response)

        self.assert_ok_create_kiddish_db(
            extra_attrs={
                'account.content_rating_class': str(TEST_CONTENT_RATING_CLASS1),
                'account.music_content_rating_class': str(TEST_CONTENT_RATING_CLASS2),
                'account.video_content_rating_class': str(TEST_CONTENT_RATING_CLASS3),
                'avatar.default': TEST_DEFAULT_AVATAR1,
                'person.birthday': TEST_BIRTHDATE1,
                'person.firstname': TEST_FIRSTNAME1.encode('utf8'),
                'person.gender': Gender.to_char(Gender.Male),
                'person.lastname': TEST_LASTNAME1.encode('utf8'),
            },
        )

        self.assert_ok_create_kiddish_event_log(
            extra_events={
                'info.birthday': TEST_BIRTHDATE1,
                'info.content_rating_class': str(TEST_CONTENT_RATING_CLASS1),
                'info.default_avatar': TEST_DEFAULT_AVATAR1,
                'info.firstname': TEST_FIRSTNAME1.encode('utf8'),
                'info.lastname': TEST_LASTNAME1.encode('utf8'),
                'info.music_content_rating_class': str(TEST_CONTENT_RATING_CLASS2),
                'info.sex': str(Gender.Male),
                'info.video_content_rating_class': str(TEST_CONTENT_RATING_CLASS3),
            },
        )

        self.assert_ok_create_kiddish_statbox_log(
            extra_lines={
                'account.content_rating_class',
                'account.music_content_rating_class',
                'account.video_content_rating_class',
                'person.birthday',
                'person.default_avatar',
                'person.firstname',
                'person.fullname',
                'person.gender',
                'person.lastname',
            },
        )

        self.assertEqual(len(self.env.blackbox.requests), 3)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_blackbox_loginoccupation_request_ok(self.env.blackbox.requests[2])

    def test_required_args(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_create_kiddish_response())

        self.assert_ok_create_kiddish_db()
        self.assert_ok_create_kiddish_event_log()
        self.assert_ok_create_kiddish_statbox_log()

        self.assertEqual(len(self.env.blackbox.requests), 3)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_blackbox_loginoccupation_request_ok(self.env.blackbox.requests[2])

    def test_no_display_name(self):
        rv = self.make_request(exclude_args=['display_name'])
        self.assert_error_response(rv, ['display_name.invalid'])

    def test_empty_display_name(self):
        rv = self.make_request(query_args=dict(display_name=''))
        self.assert_error_response(rv, ['display_name.empty'])

    def test_family_id_not_match(self):
        rv = self.make_request(query_args=dict(family_id=TEST_FAMILY_ID1))
        self.assert_error_response(rv, ['family_id.invalid'])

    def test_content_rating_class_zero(self):
        rv = self.make_request(
            query_args=dict(
                content_rating_class='0',
            ),
        )

        expected_response = deep_merge(
            self.build_create_kiddish_response(),
            dict(
                account=dict(
                    content_rating_class=0,
                ),
            ),
            dict(
                account={c + '_content_rating_class': 0 for c in all_special_content_types()}
            ),
        )
        self.assert_ok_response(rv, **expected_response)

        self.assert_ok_create_kiddish_db(
            extra_attrs={
                'account.content_rating_class': '0',
            },
        )

    @parameterized.expand([(c,) for c in all_special_content_types()])
    def test_special_rating_class_zero(self, content_type):
        rv = self.make_request(
            query_args={
                content_type + '_content_rating_class': '0',
            },
        )

        expected_response = deep_merge(
            self.build_create_kiddish_response(),
            dict(
                account={
                    content_type + '_content_rating_class': 0,
                },
            ),
        )
        self.assert_ok_response(rv, **expected_response)

        self.assert_ok_create_kiddish_db(
            extra_attrs={
                'account.%s_content_rating_class' % content_type: '0',
            },
        )

    def test_phone_number_display_name(self):
        rv = self.make_request(query_args=dict(display_name=TEST_PHONE_NUMBER1.e164))

        expected_response = deep_merge(
            self.build_create_kiddish_response(),
            dict(
                account=dict(
                    display_name=dict(
                        name=TEST_PHONE_NUMBER1.e164,
                    ),
                ),
            ),
        )
        self.assert_ok_response(rv, **expected_response)

        self.assert_ok_create_kiddish_db(
            extra_attrs={
                'account.display_name': str(DisplayName(TEST_PHONE_NUMBER1.e164)),
            }
        )


class TestNotFamilyAdmin(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestNotFamilyAdmin, self).setUp()

        self._family_to_db(
            family_id=TEST_FAMILY_ID,
            admin_uid=TEST_UID3,
            uids=[TEST_UID, TEST_UID3],
        )

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(
                    family_info=dict(
                        admin_uid=TEST_UID3,
                        family_id=TEST_FAMILY_ID,
                    ),
                ),
            ],
        )

        self.env.blackbox.set_blackbox_response_side_effect(
            'family_info',
            [
                blackbox_family_info_response(
                    family_id=TEST_FAMILY_ID,
                    admin_uid=str(TEST_UID3),
                    uids=[TEST_UID, TEST_UID3],
                    with_members_info=True,
                ),
            ]
        )

    @property
    def expected_family_members(self):
        return [
            FamilyMember(uid=TEST_UID, place=0),
            FamilyMember(uid=TEST_UID3, place=1),
            FamilyMember(uid=TEST_UID2, place=self.expected_kiddish_place),
        ]

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_create_kiddish_response())

        self.assert_ok_create_kiddish_db()
        self.assert_ok_create_kiddish_event_log()
        self.assert_ok_create_kiddish_statbox_log()

        self.assertEqual(len(self.env.blackbox.requests), 3)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_family_info_request_ok(self.env.blackbox.requests[1])
        self.assert_blackbox_loginoccupation_request_ok(self.env.blackbox.requests[2])


class UserTicketAuthorizationTestCase(UserTicketRequestMixin, AdminWithoutKidsTestCase):
    def build_create_kiddish_response(self):
        response = super(UserTicketAuthorizationTestCase, self).build_create_kiddish_response()
        return deep_merge(
            response,
            dict(
                account=dict(
                    person=dict(
                        country='us',
                        language='en',
                    ),
                ),
            ),
        )

    @property
    def kiddish_required_attributes(self):
        return merge_dicts(
            super(UserTicketAuthorizationTestCase, self).kiddish_required_attributes,
            {
                'person.country': mock.ANY,
                'person.language': mock.ANY
            },
        )


class TestUserTicketAuthorization(RequiredQueryArgsMixin, UserTicketAuthorizationTestCase):
    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_create_kiddish_response())
        self.assert_ok_create_kiddish_db()


class TestAccountNotDefaultInSession(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    AdminWithoutKidsTestCase,
):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(TestAccountNotDefaultInSession, cls).http_query_args,
            dict(multisession_uid=TEST_UID),
        )

    def setUp(self):
        super(TestAccountNotDefaultInSession, self).setUp()

        response = blackbox_sessionid_multi_response(uid=TEST_UID3)
        authorization_kwargs = dict(
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID,
            ),
        )
        response = blackbox_sessionid_multi_append_user(response=response, **authorization_kwargs)
        self.env.blackbox.set_response_side_effect('sessionid', [response])

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, check_all=False)
        self.assert_blackbox_sessionid_request_ok(self.env.blackbox.requests[0])


class TestAccountNotDefaultInUserTicket(RequiredQueryArgsMixin, UserTicketAuthorizationTestCase):
    @classproperty
    def http_query_args(cls):
        return merge_dicts(
            super(TestAccountNotDefaultInUserTicket, cls).http_query_args,
            dict(multisession_uid=TEST_UID),
        )

    def setUp(self):
        super(TestAccountNotDefaultInUserTicket, self).setUp()

        user_ticket = fake_user_ticket(
            default_uid=TEST_UID3,
            scopes=[FAMILY_MANAGE_SCOPE],
            uids=[TEST_UID3, TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, check_all=False)
        self.assert_blackbox_userinfo_request_ok(self.env.blackbox.requests[0])


class TestSessionInvalid(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestSessionInvalid, self).setUp()
        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
            ],
        )

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])


class TestUserTicketInvalid(
    UserTicketRequestMixin,
    RequiredQueryArgsMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketInvalid, self).setUp()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket(uids=[TEST_UID])])

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.invalid'])


class TestUserTicketScopeInvalid(
    UserTicketRequestMixin,
    RequiredQueryArgsMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestUserTicketScopeInvalid, self).setUp()
        user_ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=['invalid'],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['tvm_user_ticket.missing_scopes'])


class TestNoFamily(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestNoFamily, self).setUp()

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(family_info=dict()),
            ],
        )

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.does_not_exist'])


class AdminWithKidTestCase(BaseCreateKiddishTestCase):
    def setUp(self):
        super(AdminWithKidTestCase, self).setUp()

        self._family_to_db(
            family_id=TEST_FAMILY_ID,
            admin_uid=TEST_UID,
            uids=[TEST_UID, TEST_UID1],
            places=[0, 100],
        )

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(
                    family_info=dict(
                        admin_uid=TEST_UID,
                        family_id=TEST_FAMILY_ID,
                    ),
                ),
            ],
        )

        self.env.blackbox.set_blackbox_response_side_effect(
            'family_info',
            [
                blackbox_family_info_response(
                    family_id=TEST_FAMILY_ID,
                    admin_uid=str(TEST_UID),
                    uids=[TEST_UID],
                    kid_uids=[TEST_UID1],
                    with_members_info=True,
                ),
            ],
        )

    @property
    def expected_family_members(self):
        members = super(AdminWithKidTestCase, self).expected_family_members
        members.insert(1, FamilyMember(uid=TEST_UID1, place=100))
        return members

    expected_kiddish_place = 101


@with_settings_hosts(
    FAMILY_MAX_KIDS_NUMBER=1,
)
class TestAdminWithMaxKids(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    AdminWithKidTestCase,
):
    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.max_capacity'])


@with_settings_hosts(
    FAMILY_MAX_KIDS_NUMBER=2,
)
class TestAdminWithKid(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    AdminWithKidTestCase,
):
    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_create_kiddish_response())

        self.assert_ok_create_kiddish_db()
        self.assert_ok_create_kiddish_event_log()
        self.assert_ok_create_kiddish_statbox_log()


class TestUserTicketWithSessionidScope(RequiredQueryArgsMixin, UserTicketAuthorizationTestCase):
    def setUp(self):
        super(TestUserTicketWithSessionidScope, self).setUp()

        user_ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=[SESSIONID_SCOPE],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([user_ticket])

    def test(self):
        rv = self.make_request()

        self.assert_ok_response(rv, check_all=False)


class TestByFamiliyId(
    RequiredQueryArgsMixin,
    AdminWithoutKidsTestCase,
):
    def test(self):
        rv = self.make_request(query_args=dict(family_id=TEST_FAMILY_ID))

        self.assert_ok_response(rv, **self.build_create_kiddish_response())
        self.assert_ok_create_kiddish_db()

    def build_create_kiddish_response(self):
        response = super(TestByFamiliyId, self).build_create_kiddish_response()
        return deep_merge(
            response,
            dict(
                account=dict(
                    person=dict(
                        country='us',
                        language='en',
                    ),
                ),
            ),
        )

    @property
    def kiddish_required_attributes(self):
        return merge_dicts(
            super(TestByFamiliyId, self).kiddish_required_attributes,
            {
                'person.country': mock.ANY,
                'person.language': mock.ANY
            },
        )


class TestKiddishCreateKiddish(
    RequiredQueryArgsMixin,
    SessionidRequestMixin,
    BaseCreateKiddishTestCase,
):
    def setUp(self):
        super(TestKiddishCreateKiddish, self).setUp()

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(
                    aliases=dict(kiddish=TEST_KIDDISH_LOGIN1),
                    family_info=dict(
                        admin_uid=TEST_UID,
                        family_id=TEST_FAMILY_ID,
                    ),
                ),
            ],
        )

    def test(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['family.not_allowed_to_manage_kiddish'])
