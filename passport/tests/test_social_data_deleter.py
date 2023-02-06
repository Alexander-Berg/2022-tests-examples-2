# -*- cod
from __future__ import unicode_literals

from datetime import datetime
from functools import reduce
import json

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    FakeSocialApi,
    get_ok_response as social_api_ok_response,
    get_profiles_response as social_api_get_profiles_response,
    social_api_person_item,
)
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_ANT,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
    get_attr_name,
    SID_TO_SUBSCRIPTION_ATTR,
)
from passport.backend.core.models.email import Email
from passport.backend.core.services import (
    BLOCKING_SIDS,
    Service,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.birthday import Birthday
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.gender import Gender
from passport.backend.dbscripts.social_data_deleter.cli import run
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_CONSUMER1,
    TEST_EMAIL_ID1,
    TEST_EMAIL_ID2,
    TEST_FIRSTNAME1,
    TEST_LASTNAME1,
    TEST_LOGIN1,
    TEST_SOCIAL_LOGIN1,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_SOCIAL_PROFILE_ID1 = 1
TEST_SOCIAL_PROFILE_ID2 = 2
TEST_AVATAR_ID1 = '1234/5678-3232'
TEST_SOCIAL_PROVIDER_CODE1 = 'xx'
TEST_SOCIAL_PROVIDER_USERID1 = '1234'


@with_settings_hosts(
    SOCIAL_API_URL='https://social/api/',
    SOCIAL_API_CONSUMER=TEST_CONSUMER1,
    BLACKBOX_URL='https://blackbox/',
)
class TestDeleteDataObtainedFromSocialProvider(TestCase):
    def setUp(self):
        super(TestDeleteDataObtainedFromSocialProvider, self).setUp()
        self._social_api_faker = FakeSocialApi()
        self._social_api_faker.start()
        self._tvm_credentials_manager = FakeTvmCredentialsManager()
        self._tvm_credentials_manager.start()

    def tearDown(self):
        self._tvm_credentials_manager.stop()
        self._social_api_faker.stop()
        super(TestDeleteDataObtainedFromSocialProvider, self).tearDown()

    def _setup_env(self, social_profiles=None, yandex_accounts=None):
        env = dict(
            accounts=yandex_accounts or [],
            profiles=social_profiles or [],
        )
        self._setup_blackbox(env)
        self._setup_socialism(env)
        self._setup_db(env)
        self._tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    '2': {
                        'alias': 'social_api',
                        'ticket': TEST_TICKET,
                    },
                },
           ),
        )

    def _setup_blackbox(self, env):
        args_sets = [a['userinfo'] for a in env['accounts']]
        args_sets = map(self._cast_to_blackbox_kwargs, args_sets)
        response = blackbox_userinfo_response_multiple(args_sets)
        self._blackbox_faker.set_response_side_effect('userinfo', [response])

    def _setup_db(self, env):
        args_sets = [a['userinfo'] for a in env['accounts']]
        for args in args_sets:
            args = self._cast_to_blackbox_kwargs(args)
            self._db_faker.serialize(blackbox_userinfo_response(**args))

    def _setup_socialism(self, env):
        profile_arg_sets = []
        for profile in env['profiles']:
            profile = self._cast_to_profile_kwargs(profile)
            profile_args = dict(
                profile_id=profile['profile_id'],
                uid=profile['uid'],
                username=profile['username'],
            )
            person = social_api_person_item(
                profile_id=profile['profile_id'],
                firstname=profile['firstname'],
                lastname=profile['lastname'],
                email=profile['email'],
                birthday=profile['birthday'],
                gender=profile['gender'],
                nickname=profile['nickname'],
            )
            profile_args.update(dict(person=person))
            profile_arg_sets.append(profile_args)
        profiles_response = json.dumps(social_api_get_profiles_response(profile_arg_sets))
        self._social_api_faker.set_response_side_effect('get_profiles', [profiles_response])

        delete_response = json.dumps(social_api_ok_response())
        self._social_api_faker.set_response_side_effect('delete_social_data', [delete_response])

    def _build_social_profile(self, profile_id=TEST_SOCIAL_PROFILE_ID1, uid=TEST_UID1,
                              username=None, firstname=None, lastname=None,
                              nickname=None, birthday=None, gender=None, email=None):
        return dict(
            profile_id=profile_id,
            uid=uid,
            username=username,
            firstname=firstname,
            lastname=lastname,
            nickname=nickname,
            birthday=birthday,
            gender=gender,
            email=email,
        )

    def _build_portal_account(self, uid=TEST_UID1, firstname=TEST_FIRSTNAME1,
                              lastname=TEST_LASTNAME1, gender=Undefined,
                              birthday=Undefined, display_name=Undefined, emails=None,
                              avatar_id=TEST_AVATAR_ID1, subscribed_to=Undefined,
                              login=None):
        gender = gender if gender is not Undefined else Gender.Male
        birthday = birthday if birthday is not Undefined else Birthday(2018, 7, 3)
        display_name = display_name if display_name is not Undefined else DisplayName(TEST_FIRSTNAME1)
        emails = emails or []
        subscribed_to = subscribed_to if subscribed_to is not Undefined else [Service.by_slug('passport')]
        login = login or TEST_LOGIN1
        userinfo = dict(
            uid=uid,
            login=login,
            subscribed_to=subscribed_to,
            firstname=firstname,
            lastname=lastname,
            gender=gender,
            birthdate=birthday,
            display_name=display_name,
            emails=emails,
            default_avatar_key=avatar_id,
        )
        return dict(userinfo=userinfo)

    def _build_social_account(self, uid=TEST_UID1, display_name=Undefined):
        userinfo = dict(
            uid=uid,
            login=TEST_SOCIAL_LOGIN1,
            display_name=display_name,
        )
        return dict(userinfo=userinfo)

    def _cast_to_profile_kwargs(self, kwargs):
        new = dict(kwargs)
        if kwargs.get('gender'):
            new['gender'] = Gender.to_char(new['gender'])
        if kwargs.get('birthday'):
            new['birthday'] = str(kwargs['birthday'])
        return new

    def _cast_to_blackbox_kwargs(self, kwargs):
        new = dict(kwargs)

        if new.get('emails'):
            emails = new.pop('emails')
            emails = map(self._email_model_to_blackbox_attributes, emails)
            emails = reduce(deep_merge, emails, dict())
            new.update(emails)

        if new.get('display_name'):
            new['display_name'] = new['display_name'].as_dict()

        if new.get('birthdate'):
            new['birthdate'] = str(new['birthdate'])
        return new

    def _email_model_to_blackbox_attributes(self, email):
        email_attributes = dict(
            email_attributes=[
                dict(
                    id=email.id,
                    attributes={
                        EMAIL_ANT['address']: email.address,
                        EMAIL_ANT['created']: 1,
                        EMAIL_ANT['confirmed']: None if not email.confirmed_at else datetime_to_integer_unixtime(email.confirmed_at),
                        EMAIL_ANT['bound']: None if not email.bound_at else datetime_to_integer_unixtime(email.bound_at),
                        EMAIL_ANT['is_unsafe']: int(bool(email.is_unsafe)),
                    },
                ),
            ],
        )
        return email_attributes

    def _assert_account_attributes_removed(self, uid, attributes):
        for attr in attributes:
            self._db_faker.check_db_attr_missing(uid, attr)

    def _assert_account_attributes_equal(self, uid, attrs):
        for name, value in attrs.items():
            self._db_faker.check_db_attr(uid, name, value)

    def _assert_account_email_removed(self, uid, email_id, address):
        for attr_name in EMAIL_ANT:
            self._db_faker.check_db_ext_attr_missing(
                uid,
                EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                email_id,
                attr_name,
            )

    def _assert_account_has_email(self, uid, email_id, address):
        self._db_faker.check_db_ext_attr(
            uid,
            EXTENDED_ATTRIBUTES_EMAIL_TYPE,
            email_id,
            'address',
            address,
        )

    def _assert_socialism_requested_to_delete_profiles(self, profile_ids):
        self._social_api_faker.requests[1].assert_properties_equal(
            url='https://social/api/delete_social_data?consumer=%s' % TEST_CONSUMER1,
            post_args={'profile_ids': ','.join(map(str, profile_ids))},
        )

    def _assert_uids_requested_from_blackbox(self, uids):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
                'uid': ','.join(map(str, uids)),
            },
        )

    def _assert_emails_requested_from_blackbox(self):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
                'getemails': 'all',
                'email_attributes': 'all',
            },
        )

    def _assert_profiles_requested_from_socialism(self, provider_code, userid):
        self._social_api_faker.requests[0].assert_url_starts_with('https://social/api/profiles?')
        self._social_api_faker.requests[0].assert_query_contains(
            {
                'provider': provider_code,
                'userid': userid,
            },
        )

    def _assert_personal_data_requested_from_socialism(self):
        self._social_api_faker.requests[0].assert_url_starts_with('https://social/api/profiles?')
        self._social_api_faker.requests[0].assert_query_contains({'include': 'person'})

    def _assert_display_name_requested_from_blackbox(self):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
            },
        )
        eq_(self._blackbox_faker.requests[0].post_args['regname'], 'yes')

    def _assert_dbfields_requested_from_blackbox(self, dbfields):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
            },
        )
        self._blackbox_faker.requests[0].assert_contains_dbfields(dbfields)

    def _assert_attributes_requested_from_blackbox(self, attributes):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
            },
        )
        self._blackbox_faker.requests[0].assert_contains_attributes(attributes)

    def _assert_avatar_requested_from_blackbox(self):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
            },
        )
        eq_(self._blackbox_faker.requests[0].post_args['regname'], 'yes')

    def _assert_blocking_subscriptions_requested_from_blackbox(self):
        self._blackbox_faker.requests[0].assert_properties_equal(url='https://blackbox/blackbox/')
        self._blackbox_faker.requests[0].assert_post_data_contains(
            {
                'method': 'userinfo',
            },
        )

        subscription_dbfields = set()
        subscription_attrs = set()
        for sid in BLOCKING_SIDS:
            if sid in SID_TO_SUBSCRIPTION_ATTR:
                attr = get_attr_name(SID_TO_SUBSCRIPTION_ATTR[sid])
                subscription_attrs.add(attr)
            else:
                subscription_dbfields.add('subscription.suid.%s' % sid)
        self._blackbox_faker.requests[0].assert_contains_attributes(subscription_attrs)
        self._blackbox_faker.requests[0].assert_contains_dbfields(subscription_dbfields)

    def test_socialism_requested_to_delete_profiles(self):
        profiles = [
            self._build_social_profile(
                profile_id=TEST_SOCIAL_PROFILE_ID1,
                uid=TEST_UID1,
            ),
            self._build_social_profile(
                profile_id=TEST_SOCIAL_PROFILE_ID2,
                uid=TEST_UID2,
            ),
        ]
        self._setup_env(social_profiles=profiles, yandex_accounts=[])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_socialism_requested_to_delete_profiles(
            [
                TEST_SOCIAL_PROFILE_ID1,
                TEST_SOCIAL_PROFILE_ID2,
            ],
        )

    def test_userinfo_requested_from_blackbox(self):
        profiles = [
            self._build_social_profile(
                profile_id=TEST_SOCIAL_PROFILE_ID1,
                uid=TEST_UID1,
            ),
            self._build_social_profile(
                profile_id=TEST_SOCIAL_PROFILE_ID2,
                uid=TEST_UID2,
            ),
        ]
        self._setup_env(social_profiles=profiles, yandex_accounts=[])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_uids_requested_from_blackbox([TEST_UID1, TEST_UID2])
        self._assert_dbfields_requested_from_blackbox(
            {
                'userinfo.sex.uid',
            },
        )
        self._assert_attributes_requested_from_blackbox(
            {
                'person.firstname',
                'person.lastname',
                'person.birthday',
            },
        )
        self._assert_display_name_requested_from_blackbox()
        self._assert_avatar_requested_from_blackbox()
        self._assert_display_name_requested_from_blackbox()
        self._assert_emails_requested_from_blackbox()
        self._assert_blocking_subscriptions_requested_from_blackbox()

    def test_profiles_request_from_socialism(self):
        self._setup_env(social_profiles=[], yandex_accounts=[])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_profiles_requested_from_socialism(
            TEST_SOCIAL_PROVIDER_CODE1,
            TEST_SOCIAL_PROVIDER_USERID1,
        )
        self._assert_personal_data_requested_from_socialism()

    def test_no_profiles(self):
        self._setup_env(social_profiles=[], yandex_accounts=[])
        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

    def test_no_matches(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jstock68',
            firstname='Joe',
            lastname='Stockman',
            nickname='blood',
            birthday=Birthday(2018, 3, 12),
            gender=Gender.Male,
            email='jstock68@yahoo.com',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Ella',
            lastname='Fitzerald',
            gender=Gender.Female,
            birthday=Birthday(1932, 3, 12),
            display_name=DisplayName('ella'),
            emails=[
                Email(
                    id=TEST_EMAIL_ID1,
                    address='ella@yahoo.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=True,
                ),
            ],
            avatar_id=TEST_AVATAR_ID1,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(TEST_UID1, ['avatar.default'])
        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'account.display_name': str(DisplayName('ella')),
                'person.birthday': '1932-03-12',
                'person.firstname': 'Ella',
                'person.gender': Gender.to_char(Gender.Female),
                'person.lastname': 'Fitzerald',
            },
        )
        self._assert_account_has_email(TEST_UID1, TEST_EMAIL_ID1, 'ella@yahoo.com')

    def test_everything_matches(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jstock68',
            firstname='Joe',
            lastname='Stockman',
            nickname='blood',
            birthday=Birthday(2018, 3, 12),
            gender=Gender.Male,
            email='jstock68@yahoo.com',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Joe',
            lastname='Stockman',
            gender=Gender.Male,
            birthday=Birthday(2018, 3, 12),
            display_name=DisplayName('blood'),
            emails=[
                Email(
                    id=TEST_EMAIL_ID1,
                    address='jstock68@yahoo.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=True,
                ),
            ],
            avatar_id=TEST_AVATAR_ID1,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'avatar.default',
                'person.birthday',
                'person.firstname',
                'person.gender',
                'person.lastname',
            ],
        )
        self._assert_account_email_removed(TEST_UID1, TEST_EMAIL_ID1, 'jstock68@yahoo.com')

    def test_account_data_deleted(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jstock68',
            firstname='Joe',
            lastname='Stockman',
            nickname='blood',
            birthday=Birthday(2018, 3, 12),
            gender=Gender.Male,
            email='jstock68@yahoo.com',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='',
            lastname='',
            gender=Gender.Unknown,
            birthday=None,
            display_name=DisplayName(''),
            emails=[],
            avatar_id=None,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'avatar.default',
                'person.birthday',
                'person.firstname',
                'person.gender',
                'person.lastname',
            ],
        )

    def test_user_has_contract_with_yandex(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            firstname='Joe',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Joe',
            avatar_id=TEST_AVATAR_ID1,
            subscribed_to=[Service.by_slug('balance')],
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'avatar.default': TEST_AVATAR_ID1,
                'person.firstname': 'Joe',
            },
        )

    def test_profile_empty(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Joe',
            lastname='Stockman',
            gender=Gender.Male,
            birthday=Birthday(2018, 3, 12),
            display_name=DisplayName('blood'),
            emails=[
                Email(
                    id=TEST_EMAIL_ID1,
                    address='jstock68@yahoo.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=True,
                ),
            ],
            avatar_id=TEST_AVATAR_ID1,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(TEST_UID1, ['avatar.default'])
        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'account.display_name': str(DisplayName('blood')),
                'person.birthday': '2018-03-12',
                'person.firstname': 'Joe',
                'person.gender': Gender.to_char(Gender.Male),
                'person.lastname': 'Stockman',
            },
        )
        self._assert_account_has_email(TEST_UID1, TEST_EMAIL_ID1, 'jstock68@yahoo.com')

    def test_profile_username_equals_to_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jim',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='jim',
            lastname='jim',
            display_name=DisplayName('jim'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_username_part_of_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='korn',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Korney',
            lastname='Rokorn',
            display_name=DisplayName('**KoRn!**'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_firstname_equals_to_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            firstname='Ann',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Ann',
            lastname='Ann',
            display_name=DisplayName('ann'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_firstname_part_of_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            firstname='John',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Johnatan',
            lastname='Arjohns',
            display_name=DisplayName('SuperJohn'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_lastname_equals_to_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            lastname='Owe',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Owe',
            lastname='Owe',
            display_name=DisplayName('owe'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_lastname_part_of_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            lastname='Ocean',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Mocean',
            lastname='Oceaner',
            display_name=DisplayName('D.Ocean123'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_nickname_equals_to_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            nickname='doc',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Doc',
            lastname='Doc',
            display_name=DisplayName('doc'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_profile_nickname_part_of_all_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            nickname='korn',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='Korney',
            lastname='Rokorn',
            display_name=DisplayName('**KoRn!**'),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
                'person.lastname',
            ],
        )

    def test_short_profile_name_not_equal_to_account_names(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jst',
            firstname='Joh',
            lastname='Sto',
            nickname='blo',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='John',
            lastname='Stockman',
            display_name=DisplayName('jstblo'),
            avatar_id=TEST_AVATAR_ID1,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(TEST_UID1, ['avatar.default'])
        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'account.display_name': str(DisplayName('jstblo')),
                'person.firstname': 'John',
                'person.lastname': 'Stockman',
            },
        )

    @parameterized.expand([
        [Birthday(2018, 3, 12)],
        [Birthday(0, 3, 12)],
        [Birthday(2018, 0, 0)],
        [Birthday(0, 0, 12)],
        [Birthday(0, 3, 0)],
    ])
    def test_zero_profile_birthday(self, account_birthday):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            birthday=Birthday(0, 0, 0),
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            birthday=account_birthday,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'person.birthday': str(account_birthday),
            },
        )

    @parameterized.expand([
        [Birthday(2018, 0, 0)],
        [Birthday(2018, 3, 2)],
        [Birthday(2018, 3, 0)],
        [Birthday(2018, 4, 1)],
        [Birthday(2018, 0, 1)],
        [Birthday(2017, 3, 1)],
        [Birthday(0000, 3, 1)],
        ['invalid'],
        [''],
    ])
    def test_profile_birthday_not_matches_to_account(self, profile_birthday):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            birthday=profile_birthday,
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            birthday=Birthday(2018, 3, 1),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'person.birthday': '2018-03-01',
            },
        )

    def test_gender_not_match(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            gender=Gender.Male,
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            gender=Gender.Female,
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_equal(
            TEST_UID1,
            {
                'person.gender': Gender.to_char(Gender.Female),
            },
        )

    def test_safe_email(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            email='jstock68@yahoo.com',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            emails=[
                Email(
                    id=TEST_EMAIL_ID1,
                    address='jstock68@yahoo.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=False,
                ),
            ],
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_has_email(TEST_UID1, TEST_EMAIL_ID1, 'jstock68@yahoo.com')

    def test_many_emails(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            email='jstock68@yahoo.com',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            emails=[
                Email(
                    id=TEST_EMAIL_ID1,
                    address='jstock68@yahoo.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=True,
                ),
                Email(
                    id=TEST_EMAIL_ID2,
                    address='jstock68@aol.com',
                    confirmed_at=datetime.now(),
                    is_unsafe=True,
                ),
            ],
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_email_removed(TEST_UID1, TEST_EMAIL_ID1, 'jstock68@yahoo.com')
        self._assert_account_has_email(TEST_UID1, TEST_EMAIL_ID2, 'jstock68@aol.com')

    def test_social_display_name(self):
        profile = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='blood',
        )
        account = self._build_social_account(
            uid=TEST_UID1,
            display_name=DisplayName('blood', 'vk', TEST_SOCIAL_PROFILE_ID1),
        )
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
            ],
        )

    def test_many_profiles(self):
        profile1 = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jstock68',
        )
        profile2 = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID2,
            uid=TEST_UID1,
            username='batman71',
        )
        account = self._build_portal_account(
            uid=TEST_UID1,
            firstname='jstock68',
            display_name=DisplayName('batman71'),
        )
        self._setup_env(social_profiles=[profile1, profile2], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
            ],
        )

    def test_many_accounts(self):
        profile1 = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID1,
            uid=TEST_UID1,
            username='jstock68',
        )
        profile2 = self._build_social_profile(
            profile_id=TEST_SOCIAL_PROFILE_ID2,
            uid=TEST_UID2,
            username='batman71',
        )
        account1 = self._build_portal_account(
            uid=TEST_UID1,
            firstname='jstock68',
            login='hello',
            display_name=DisplayName('batman71'),
        )
        account2 = self._build_portal_account(
            uid=TEST_UID2,
            firstname='jstock68',
            login='yello',
            display_name=DisplayName('batman71'),
        )
        self._setup_env(
            social_profiles=[profile1, profile2],
            yandex_accounts=[account1, account2],
        )

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_removed(
            TEST_UID1,
            [
                'account.display_name',
                'person.firstname',
            ],
        )
        self._assert_account_attributes_removed(
            TEST_UID2,
            [
                'account.display_name',
                'person.firstname',
            ],
        )

    def test_global_logout(self):
        profile = self._build_social_profile(uid=TEST_UID1)
        account = self._build_portal_account(uid=TEST_UID1)
        self._setup_env(social_profiles=[profile], yandex_accounts=[account])

        run(TEST_SOCIAL_PROVIDER_CODE1, TEST_SOCIAL_PROVIDER_USERID1)

        self._assert_account_attributes_equal(
            TEST_UID1,
            {'account.global_logout_datetime': TimeNow()},
        )
