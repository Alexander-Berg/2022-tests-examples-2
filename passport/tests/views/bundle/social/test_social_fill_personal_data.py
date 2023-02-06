# -*- coding: utf-8 -*-

from datetime import datetime
from functools import partial
from itertools import product

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core import Undefined
from passport.backend.core.builders.avatars_mds_api.faker import avatars_mds_api_upload_ok_response
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_profiles_no_profiles,
    get_profiles_response,
    task_data_response,
    task_not_found_error,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_ANT
from passport.backend.core.models.email import Email
from passport.backend.core.test.consts import (
    TEST_BIRTHDATE1,
    TEST_BIRTHDATE2,
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_EMAIL_ID1,
    TEST_EMAIL_ID2,
    TEST_FIRSTNAME1,
    TEST_FIRSTNAME2,
    TEST_LASTNAME1,
    TEST_LASTNAME2,
    TEST_SOCIAL_AVATAR1,
    TEST_SOCIAL_TASK_ID1,
    TEST_TRACK_ID1,
    TEST_UID,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_GROUP_ID = '1234'


@nottest
class TestSocialFillPersonalData(BaseBundleTestViews):
    def setUp(self):
        super(TestSocialFillPersonalData, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value({
            'dev': {
                'grants': {'social': ['fill_personal_data']},
                'networks': ['127.0.0.1'],
            },
        })
        self._track_manager = self.env.track_manager.get_manager()
        self._track_id = TEST_TRACK_ID1
        self._authentication_headers = dict()

        self._setup_statbox_templates()

    def tearDown(self):
        del self._track_manager
        self.env.stop()
        del self.env
        super(TestSocialFillPersonalData, self).tearDown()

    @property
    def http_headers(self):
        headers = dict(
            user_agent='curl',
            user_ip=TEST_USER_IP1,
            host=None,
        )
        headers.update(self._authentication_headers)
        return headers

    def _build_sessionid_authentication(self):
        return dict(
            host='passport.yandex.ru',
            cookie='Session_id=Session_id;',
        )

    def _build_token_authentication(self):
        return dict(authorization='OAuth authn_token')

    def _setup_authentication(self, authentication=None, **kwargs):
        if authentication is None:
            authentication = self._build_sessionid_authentication()

        self._authentication_headers = authentication

    def _setup_account(self,
                       account_firstname=TEST_FIRSTNAME2,
                       account_lastname=TEST_LASTNAME2,
                       account_birthday=TEST_BIRTHDATE2,
                       account_has_avatar=True,
                       account_email=Undefined,
                       account_uid=TEST_UID1,
                       account_token_scope=X_TOKEN_OAUTH_SCOPE,
                       account_authentication_is_invalid=False,
                       account_gender='f',
                       userinfo_kwargs=None,
                       **kwargs):
        account = dict()

        if account_gender == 'u':
            account_gender = 0
        elif account_gender == 'f':
            account_gender = 2

        account['userinfo'] = dict(
            uid=account_uid,
            firstname=account_firstname,
            lastname=account_lastname,
            birthdate=account_birthday,
            gender=account_gender,
        )
        if not account_has_avatar:
            account['userinfo'].update(
                dict(
                    default_avatar_key='0/0-0',
                    is_avatar_empty=True,
                ),
            )
        if account_email is Undefined:
            account_email = Email(
                id=TEST_EMAIL_ID2,
                address=TEST_EMAIL2,
                is_native=False,
                confirmed_at=datetime.now(),
                is_silent=False,
            )
        if account_email is not None:
            email_attributes = self._email_model_to_blackbox_attributes(account_email)
            account['userinfo'].update(email_attributes)

        if not account_authentication_is_invalid:
            account['sessionid'] = dict()
        else:
            account['sessionid'] = dict(status=BLACKBOX_SESSIONID_INVALID_STATUS)

        if not account_authentication_is_invalid:
            account['oauth'] = dict(scope=account_token_scope)
        else:
            account['oauth'] = dict(status=BLACKBOX_OAUTH_INVALID_STATUS)

        if userinfo_kwargs is not None:
            account['userinfo'].update(userinfo_kwargs)

        sessionid_args = deep_merge(account['userinfo'], account['sessionid'])
        sessionid_response = blackbox_sessionid_multi_response(**sessionid_args)
        self.env.blackbox.set_response_value('sessionid', sessionid_response)

        oauth_args = deep_merge(account['userinfo'], account['oauth'])
        oauth_response = blackbox_oauth_response(**oauth_args)
        self.env.blackbox.set_response_value('oauth', oauth_response)

        self.env.db.serialize(blackbox_userinfo_response(**account['userinfo']))

    def _email_model_to_blackbox_attributes(self, email):
        if email.is_native:
            email_attributes = dict(
                emails=[
                    dict(
                        address=email.address,
                        native=email.is_native,
                        validated=email.is_confirmed or None,
                        silent=email.is_silent,
                    ),
                ],
            )
        else:
            email_attributes = dict(
                email_attributes=[
                    dict(
                        id=email.id,
                        attributes={
                            EMAIL_ANT['address']: email.address,
                            EMAIL_ANT['created']: 1,
                            EMAIL_ANT['confirmed']: None if not email.confirmed_at else datetime_to_integer_unixtime(email.confirmed_at),
                            EMAIL_ANT['is_silent']: email.is_silent,
                            EMAIL_ANT['bound']: None if not email.bound_at else datetime_to_integer_unixtime(email.bound_at),
                        },
                    ),
                ],
            )
        return email_attributes

    def _setup_profile(self,
                       task_exists=True,
                       profile_exists=True,
                       provider_code='gg',
                       profile_firstname=TEST_FIRSTNAME1,
                       profile_lastname=TEST_LASTNAME1,
                       profile_birthday=TEST_BIRTHDATE1,
                       profile_avatar=TEST_SOCIAL_AVATAR1,
                       profile_email=TEST_EMAIL1,
                       profile_gender='f',
                       **kwargs):
        if task_exists:
            task_response = task_data_response(
                provider_code=provider_code,
                firstname=profile_firstname,
                lastname=profile_lastname,
                birthday=profile_birthday,
                avatar=profile_avatar,
                email=profile_email,
                gender=profile_gender,
            )
        else:
            task_response = task_not_found_error()
        self.env.social_api.set_response_value('get_task_data', task_response)

        if profile_exists:
            profiles_response = get_profiles_response()
        else:
            profiles_response = get_profiles_no_profiles()
        self.env.social_api.set_response_value('get_profiles', profiles_response)

    def _setup_track(self, track_exists=True, **kwargs):
        if not track_exists:
            return

        self._track_id = self.env.track_manager.create_test_track(self._track_manager, 'authorize')
        with self._track_manager.transaction(self._track_id).rollback_on_error() as track:
            self._populate_track(track, **kwargs)

    def _populate_track(self, track):
        raise NotImplementedError()  # pragma: no cover

    def _setup_all(self, **kwargs):
        self._setup_track(**kwargs)
        self._setup_authentication(**kwargs)
        self._setup_account(**kwargs)
        self._setup_profile(**kwargs)

    def _assert_sessionid_checked(self):
        request = self.env.blackbox.requests[0]
        request.assert_query_contains(
            dict(
                method='sessionid',
                sessionid='Session_id',
                host='passport.yandex.ru',
                userip=TEST_USER_IP1,
            ),
        )

    def _assert_token_checked(self):
        request = self.env.blackbox.requests[0]
        request.assert_query_contains(
            dict(
                method='oauth',
                oauth_token='authn_token',
                userip=TEST_USER_IP1,
            ),
        )

    def _assert_firstname_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_contains_attributes({'person.firstname'})

    def _assert_lastname_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_contains_attributes({'person.lastname'})

    def _assert_emails_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_query_contains(
            dict(
                emails='getall',
                getemails='all',
                email_attributes='all',
            ),
        )

    def _assert_avatar_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_query_contains(dict(regname='yes'))

    def _assert_birthday_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_contains_attributes({'person.birthday'})

    def _assert_gender_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_contains_dbfields({'userinfo.sex.uid'})

    def _assert_all_account_attributes_requested(self):
        self._assert_firstname_requested()
        self._assert_lastname_requested()
        self._assert_gender_requested()
        self._assert_birthday_requested()
        self._assert_avatar_requested()
        self._assert_emails_requested()

    def _setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'internal',
            uid=str(TEST_UID1),
            consumer='dev',
            ip=TEST_USER_IP1,
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'external',
            _inherit_from='internal',
            mode='fill_account_from_social_profile',
            track_id=self._get_track_id,
            provider='gg',
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='external',
            step='commit',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'committed',
            _inherit_from='external',
            step='commit',
            action='committed',
        )

    def _get_track_id(self):
        return self._track_id

    def test_no_track_id(self):
        self._setup_all()

        rv = self.make_request(query_args=dict(track_id=None))

        self.assert_error_response(rv, ['track_id.empty'])

    def test_no_track(self):
        self._setup_all(track_exists=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.not_found'])

    def test_no_task(self):
        self._setup_all(task_exists=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['task.not_found'])

    def test_profile_not_bound_to_account(self):
        self._setup_all(profile_exists=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['social_profile.invalid'])

    def test_track_not_contain_uid(self):
        self._setup_all(track_uid=None)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_track_contains_invalid_uid(self):
        self._setup_all(account_uid=TEST_UID1, track_uid=TEST_UID2)

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.no_uid'])

    def test_token_not_has_xtoken_grant(self):
        self._setup_all(
            authentication=self._build_token_authentication(),
            account_token_scope='oauth:grant_fake',
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_token_invalid(self):
        self._setup_all(
            authentication=self._build_token_authentication(),
            account_authentication_is_invalid=True,
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_session_invalid(self):
        self._setup_all(
            authentication=self._build_sessionid_authentication(),
            account_authentication_is_invalid=True,
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])


@istest
@with_settings_hosts
class TestSocialFillPersonalDataSubmit(TestSocialFillPersonalData):
    default_url = '/1/bundle/social/fill_personal_data/submit/'
    http_method = 'get'

    @property
    def http_query_args(self):
        return dict(
            consumer='dev',
            task_id=TEST_SOCIAL_TASK_ID1,
            track_id=self._track_id,
        )

    def _populate_track(self, track, track_uid=TEST_UID1, **kwargs):
        track.uid = track_uid

    def _setup_statbox_templates(self):
        super(TestSocialFillPersonalDataSubmit, self)._setup_statbox_templates()

        self.env.statbox.bind_entry('submitted', step='submit', _inherit_from='submitted')
        self.env.statbox.bind_entry('committed', step='submit', _inherit_from='committed')

    def _get_response_data(self,
                           provider_code='gg',
                           firstname=None,
                           lastname=None,
                           birthday=None,
                           avatar=None,
                           email=None,
                           gender=None):
        values = dict()
        if firstname is not None:
            values['firstname'] = firstname
        if lastname is not None:
            values['lastname'] = lastname
        if birthday is not None:
            values['birthday'] = birthday
        if avatar is not None:
            values['avatar'] = avatar
        if email is not None:
            values['email'] = email
        if gender is not None:
            values['gender'] = gender
        return [
            {
                'source': {'provider_code': provider_code},
                'values': values,
            },
        ]

    def test_no_task_id(self):
        self._setup_all()

        rv = self.make_request(query_args=dict(task_id=None))

        self.assert_error_response(rv, ['task_id.empty'])

    def test_session_ok(self):
        self._setup_all()

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data())
        self._assert_sessionid_checked()
        self._assert_all_account_attributes_requested()

    def test_token_ok(self):
        self._setup_all(authentication=self._build_token_authentication())

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data())
        self._assert_token_checked()
        self._assert_all_account_attributes_requested()

    def test_provider(self):
        self._setup_all(provider_code='xx')

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(provider_code='xx'))

    def test_no_firstname(self):
        self._setup_all(
            profile_firstname=None,
            account_firstname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(firstname=None))

    def test_firstname__account_has_no_firstname(self):
        self._setup_all(
            profile_firstname=TEST_FIRSTNAME1,
            account_firstname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(firstname=TEST_FIRSTNAME1))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('committed'),
        ])

    def test_firstname__account_has_firstname(self):
        self._setup_all(
            profile_firstname=TEST_FIRSTNAME1,
            account_firstname=TEST_FIRSTNAME2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(firstname=None))

    def test_no_lastname(self):
        self._setup_all(
            profile_lastname=None,
            account_lastname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(lastname=None))

    def test_lastname__account_has_no_lastname(self):
        self._setup_all(
            profile_lastname=TEST_LASTNAME1,
            account_lastname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(lastname=TEST_LASTNAME1))

    def test_lastname__account_has_lastname(self):
        self._setup_all(
            profile_lastname=TEST_LASTNAME1,
            account_lastname=TEST_LASTNAME2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(lastname=None))

    def test_no_gender(self):
        self._setup_all(
            profile_gender=None,
            account_gender=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(gender=None))

    def test_gender__account_has_no_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(gender='m'))

    def test_gender_account_has_unknown_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender='u',
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(gender='m'))

    def test_gender__account_has_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender='f',
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(gender=None))

    def test_no_birthday(self):
        self._setup_all(
            profile_birthday=None,
            account_birthday=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(birthday=None))

    def test_birthday__account_has_no_birthday(self):
        self._setup_all(
            profile_birthday=TEST_BIRTHDATE1,
            account_birthday=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(birthday=TEST_BIRTHDATE1))

    def test_birthday__account_has_birthday(self):
        self._setup_all(
            profile_birthday=TEST_BIRTHDATE1,
            account_birthday=TEST_BIRTHDATE2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(birthday=None))

    def test_no_avatar(self):
        self._setup_all(
            profile_avatar=None,
            account_has_avatar=False,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(avatar=None))

    def test_avatar__account_has_no_avatar(self):
        self._setup_all(
            profile_avatar=TEST_SOCIAL_AVATAR1,
            account_has_avatar=False,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(avatar=TEST_SOCIAL_AVATAR1))

    def test_avatar__account_has_avatar(self):
        self._setup_all(
            profile_avatar=TEST_SOCIAL_AVATAR1,
            account_has_avatar=True,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(avatar=None))

    def test_no_email(self):
        self._setup_all(
            profile_email=None,
            account_email=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email=None))

    @parameterized.expand([
        (e, c, s) for e, c, s in product([False, True], repeat=3)
        if (e, c, s) != (True, True, False)
    ])
    def test_email__account_has_other_not_suitable_email(self, is_external, is_confirmed, is_silent):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=not is_external,
            confirmed_at=None if not is_confirmed else datetime.now(),
            is_silent=is_silent,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email=TEST_EMAIL1))

    @parameterized.expand([(e, c, s) for e, c, s in product([False, True], repeat=3)])
    def test_email__account_has_same_email(self, is_external, is_confirmed, is_silent):
        account_email = Email(
            id=TEST_EMAIL_ID1,
            address=TEST_EMAIL1,
            is_native=not is_external,
            confirmed_at=None if not is_confirmed else datetime.now(),
            is_silent=is_silent,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email=None))

    def test_email__account_has_other_suitable_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=False,
            confirmed_at=datetime.now(),
            is_silent=False,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email=None))

    def test_native_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=True,
            confirmed_at=datetime.now(),
            is_silent=False,
        )
        self._setup_all(
            profile_email=TEST_EMAIL2,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email=None))

    def test_friend_native_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address='my@yandex.ru',
            is_native=True,
            confirmed_at=datetime.now(),
            is_silent=False,
        )
        self._setup_all(
            profile_email='friend@yandex.ru',
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, data=self._get_response_data(email='friend@yandex.ru'))


@istest
@with_settings_hosts()
class TestSocialFillPersonalDataCommit(TestSocialFillPersonalData):
    default_url = '/1/bundle/social/fill_personal_data/commit/?consumer=dev'
    http_method = 'post'

    @property
    def http_query_args(self):
        return dict(track_id=self._track_id)

    def _populate_track(self,
                        track,
                        track_uid=TEST_UID1,
                        track_task_id=TEST_SOCIAL_TASK_ID1,
                        **kwargs):
        track.uid = track_uid
        track.social_task_id = track_task_id

    def _setup_all(self, **kwargs):
        super(TestSocialFillPersonalDataCommit, self)._setup_all(**kwargs)
        self._setup_avatars_mds_api()

    def _setup_avatars_mds_api(self):
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response(TEST_GROUP_ID))

    def _setup_statbox_templates(self):
        super(TestSocialFillPersonalDataCommit, self)._setup_statbox_templates()

        self.env.statbox.bind_entry('submitted', step='commit', _inherit_from='submitted')
        self.env.statbox.bind_entry('committed', step='commit', _inherit_from='committed')
        self.env.statbox.bind_entry(
            'person_attribute_created',
            _inherit_from='internal',
            event='account_modification',
            old='-',
            operation='created',
        )
        self.env.statbox.bind_entry(
            'firstname_created',
            _inherit_from='person_attribute_created',
            entity='person.firstname',
            new=TEST_FIRSTNAME1,
        )
        self.env.statbox.bind_entry(
            'fullname_updated',
            _inherit_from='person_attribute_created',
            entity='person.fullname',
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'lastname_created',
            _inherit_from='person_attribute_created',
            entity='person.lastname',
            new=TEST_LASTNAME1,
        )
        self.env.statbox.bind_entry(
            'gender_created',
            _inherit_from='person_attribute_created',
            entity='person.gender',
            new='m',
        )
        self.env.statbox.bind_entry(
            'birthday_created',
            _inherit_from='person_attribute_created',
            entity='person.birthday',
            new=TEST_BIRTHDATE1,
        )
        self.env.statbox.bind_entry(
            'email_added',
            _inherit_from='person_attribute_created',
            entity='account.emails',
            email_id='1',
            operation='added',
            is_native='0',
            is_silent='0',
            is_unsafe='1',
            is_suitable_for_restore='0',
            new=mask_email_for_statbox(TEST_EMAIL1),
            created_at=partial(DatetimeNow, convert_to_datetime=True),
            bound_at=partial(DatetimeNow, convert_to_datetime=True),
            confirmed_at=partial(DatetimeNow, convert_to_datetime=True),
        )

    def _assert_account_firstname_equals(self, expected):
        self._assert_account_attribute_equals('person.firstname', expected)

    def _assert_account_lastname_equals(self, expected):
        self._assert_account_attribute_equals('person.lastname', expected)

    def _assert_account_gender_equals(self, expected):
        self._assert_account_attribute_equals('person.gender', expected)

    def _assert_account_birthday_equals(self, expected):
        self._assert_account_attribute_equals('person.birthday', expected)

    def _assert_account_attribute_equals(self, attr, expected):
        if expected is not None:
            self.env.db.check_db_attr(TEST_UID1, attr, expected.encode('utf-8'))
        else:
            self.env.db.check_db_attr_missing(TEST_UID1, attr)

    def _assert_avatars_mds_api_not_requested_to_change_avatar(self):
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def _assert_avatar_uploaded_to_mds(self):
        eq_(len(self.env.avatars_mds_api.requests), 1)

    def _assert_account_has_email(self, email):
        assert not email.is_native

        uid = TEST_UID1

        if email.bound_at is Undefined:
            email.bound_at = DatetimeNow()

        if email.confirmed_at is Undefined:
            email.confirmed_at = DatetimeNow()

        if email.is_unsafe is Undefined:
            email.is_unsafe = True

        from passport.backend.core.mailer.faker.mail_utils import EmailDatabaseMatcher

        email_matcher = EmailDatabaseMatcher(self.env.db, uid, email)
        email_matcher.match('address')
        email_matcher.match('confirmed_at')
        email_matcher.match('bound_at')
        email_matcher.match('is_unsafe')
        email_matcher.match('is_silent')
        email_matcher.match('is_rpop')

    def _assert_account_not_have_email(self, address):
        self.env.db.check_missing(
            'email_bindings',
            uid=TEST_UID,
            address=address,
            db='passportdbshard1',
        )

    def _assert_account_not_have_emails(self):
        eq_(self.env.db.select('email_bindings', db='passportdbshard1'), [])

    def _assert_firstname_logged_to_historydb(self, firstname):
        expected = self._get_common_historydb_records()
        expected.update({'info.firstname': firstname.encode('utf-8')})
        self.env.event_logger.assert_events_are_logged(expected)

    def _assert_lastname_logged_to_historydb(self, lastname):
        expected = self._get_common_historydb_records()
        expected.update({'info.lastname': lastname.encode('utf-8')})
        self.env.event_logger.assert_events_are_logged(expected)

    def _assert_gender_logged_to_historydb(self, gender):
        expected = self._get_common_historydb_records()
        if gender == 'm':
            gender = '1'
        expected.update({'info.sex': gender})
        self.env.event_logger.assert_events_are_logged(expected)

    def _assert_birthday_logged_to_historydb(self, birthday):
        expected = self._get_common_historydb_records()
        expected.update({'info.birthday': birthday})
        self.env.event_logger.assert_events_are_logged(expected)

    def _assert_email_logged_to_historydb(self, email):
        expected = self._get_common_historydb_records()
        expected.update({
            'email.1': 'created',
            'email.1.address': email.address,
            'email.1.bound_at': TimeNow(),
            'email.1.confirmed_at': TimeNow(),
            'email.1.created_at': TimeNow(),
            'email.1.is_native': '0',
            'email.1.is_silent': '0',
            'email.1.is_unsafe': '1',
        })
        self.env.event_logger.assert_events_are_logged(expected)

    def _get_common_historydb_records(self):
        return {
            'action': 'fill_account_from_social_profile',
            'consumer': 'dev',
            'user_agent': 'curl',
        }

    def _assert_email_logged_to_statbox(self, email):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('email_added', new=mask_email_for_statbox(email.address)),
            self.env.statbox.entry('committed'),
        ])

    def _assert_birthday_logged_to_statbox(self, birthday):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('birthday_created', new=birthday),
            self.env.statbox.entry('committed'),
        ])

    def _assert_gender_logged_to_statbox(self, gender):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('gender_created', new=gender),
            self.env.statbox.entry('committed'),
        ])

    def _assert_lastname_logged_to_statbox(self, lastname):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('lastname_created', new=lastname),
            self.env.statbox.entry(
                'fullname_updated',
                old=TEST_FIRSTNAME2,
                new=u'{} {}'.format(TEST_FIRSTNAME2, TEST_LASTNAME1),
            ),
            self.env.statbox.entry('committed'),
        ])

    def _assert_firstname_logged_to_statbox(self, firstname):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('firstname_created', new=firstname),
            self.env.statbox.entry(
                'fullname_updated',
                old=TEST_LASTNAME2,
                new=u'{} {}'.format(TEST_FIRSTNAME1, TEST_LASTNAME2),
            ),
            self.env.statbox.entry('committed'),
        ])

    def test_track_not_contain_task_id(self):
        self._setup_all(track_task_id=None)

        rv = self.make_request()

        self.assert_error_response(rv, ['task.not_found'])

    def test_session_ok(self):
        self._setup_all()

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_sessionid_checked()
        self._assert_all_account_attributes_requested()

    def test_token_ok(self):
        self._setup_all(authentication=self._build_token_authentication())

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_token_checked()
        self._assert_all_account_attributes_requested()

    def test_no_firstname(self):
        self._setup_all(
            profile_firstname=None,
            account_firstname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_firstname_equals(None)

    def test_firstname__account_has_no_firstname(self):
        self._setup_all(
            profile_firstname=TEST_FIRSTNAME1,
            account_firstname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_firstname_equals(TEST_FIRSTNAME1)
        self._assert_firstname_logged_to_statbox(TEST_FIRSTNAME1)
        self._assert_firstname_logged_to_historydb(TEST_FIRSTNAME1)

    def test_firstname__account_has_firstname(self):
        self._setup_all(
            profile_firstname=TEST_FIRSTNAME1,
            account_firstname=TEST_FIRSTNAME2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_firstname_equals(TEST_FIRSTNAME2)

    def test_no_lastname(self):
        self._setup_all(
            profile_lastname=None,
            account_lastname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_lastname_equals(None)

    def test_lastname__account_has_no_lastname(self):
        self._setup_all(
            profile_lastname=TEST_LASTNAME1,
            account_lastname=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_lastname_equals(TEST_LASTNAME1)
        self._assert_lastname_logged_to_statbox(TEST_LASTNAME1)
        self._assert_lastname_logged_to_historydb(TEST_LASTNAME1)

    def test_lastname__account_has_lastname(self):
        self._setup_all(
            profile_lastname=TEST_LASTNAME1,
            account_lastname=TEST_LASTNAME2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_lastname_equals(TEST_LASTNAME2)

    def test_no_gender(self):
        self._setup_all(
            profile_gender=None,
            account_gender=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_gender_equals(None)

    def test_gender__account_has_no_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_gender_equals('m')
        self._assert_gender_logged_to_statbox('m')
        self._assert_gender_logged_to_historydb('m')

    def test_gender_account_has_unknown_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender='u',
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_gender_equals('m')
        self._assert_gender_logged_to_statbox('m')
        self._assert_gender_logged_to_historydb('m')

    def test_gender__account_has_gender(self):
        self._setup_all(
            profile_gender='m',
            account_gender='f',
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_gender_equals('f')

    def test_no_birthday(self):
        self._setup_all(
            profile_birthday=None,
            account_birthday=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_birthday_equals(None)

    def test_birthday__account_has_no_birthday(self):
        self._setup_all(
            profile_birthday=TEST_BIRTHDATE1,
            account_birthday=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_birthday_equals(TEST_BIRTHDATE1)
        self._assert_birthday_logged_to_statbox(TEST_BIRTHDATE1)
        self._assert_birthday_logged_to_historydb(TEST_BIRTHDATE1)

    def test_birthday__account_has_birthday(self):
        self._setup_all(
            profile_birthday=TEST_BIRTHDATE1,
            account_birthday=TEST_BIRTHDATE2,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_birthday_equals(TEST_BIRTHDATE2)

    def test_no_avatar(self):
        self._setup_all(
            profile_avatar=None,
            account_has_avatar=False,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_avatars_mds_api_not_requested_to_change_avatar()

    def test_avatar__account_has_no_avatar(self):
        self._setup_all(
            profile_avatar=TEST_SOCIAL_AVATAR1,
            account_has_avatar=False,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_avatar_uploaded_to_mds()

        # В Статбокс и ХисториБД пишет Yapic
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_avatar__account_has_avatar(self):
        self._setup_all(
            profile_avatar=TEST_SOCIAL_AVATAR1,
            account_has_avatar=True,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_avatars_mds_api_not_requested_to_change_avatar()

    def test_invalid_avatar_format(self):
        self._setup_all(
            profile_avatar='hello',
            account_has_avatar=False,
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['exception.unhandled'])

    def test_no_email(self):
        self._setup_all(
            profile_email=None,
            account_email=None,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_not_have_emails()

    @parameterized.expand([
        (e, c, s) for e, c, s in product([False, True], repeat=3)
        if (e, c, s) != (True, True, False)
    ])
    def test_email__account_has_other_not_suitable_email(self, is_external, is_confirmed, is_silent):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=not is_external,
            confirmed_at=None if not is_confirmed else datetime.now(),
            is_silent=is_silent,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_has_email(Email(id=1, address=TEST_EMAIL1))

    @parameterized.expand([(e, c, s) for e, c, s in product([False, True], repeat=3)])
    def test_email__account_has_same_email(self, is_external, is_confirmed, is_silent):
        confirmed_at = None if not is_confirmed else datetime.now()

        account_email = Email(
            id=TEST_EMAIL_ID1,
            address=TEST_EMAIL1,
            is_native=not is_external,
            confirmed_at=confirmed_at,
            bound_at=confirmed_at,
            is_silent=is_silent,
            is_unsafe=False,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)

        if is_external:
            self._assert_account_has_email(account_email)
        else:
            self._assert_account_not_have_email(account_email.address)

    def test_email__account_has_other_suitable_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=False,
            bound_at=datetime.now(),
            confirmed_at=datetime.now(),
            is_silent=False,
            is_unsafe=False,
        )
        self._setup_all(
            profile_email=TEST_EMAIL1,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_has_email(account_email)
        self._assert_account_not_have_email(TEST_EMAIL1)

    def test_native_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address=TEST_EMAIL2,
            is_native=True,
            confirmed_at=datetime.now(),
            is_silent=False,
        )
        self._setup_all(
            profile_email=TEST_EMAIL2,
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_not_have_email(TEST_EMAIL2)

    def test_friend_native_email(self):
        account_email = Email(
            id=TEST_EMAIL_ID2,
            address='my@yandex.ru',
            is_native=True,
            confirmed_at=datetime.now(),
            is_silent=False,
        )
        self._setup_all(
            profile_email='friend@yandex.ru',
            account_email=account_email,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_has_email(Email(id=1, address='friend@yandex.ru'))
        self._assert_email_logged_to_statbox(Email(address='friend@yandex.ru'))
        self._assert_email_logged_to_historydb(Email(address='friend@yandex.ru'))

    def test_emails_over_limit(self):
        self._setup_all(
            profile_email='new@yandex.ru',
            account_email=None,
            userinfo_kwargs=dict(email_attributes=[
                {
                    'id': i,
                    'attributes': {
                        EMAIL_ANT['address']: u'test_{}@another-yandex.ru'.format(i),
                    },
                } for i in range(100)
            ]),
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_account_not_have_email(address='new@yandex.ru')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('committed'),
        ])
