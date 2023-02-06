# -*- coding: utf-8 -*-

from copy import copy
import json

from nose.tools import eq_
from passport.backend.api.views.bundle.auth.social.base import OUTPUT_MODE_SESSIONID
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_lrandoms_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth.faker import token_response
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_profiles_response,
)
from passport.backend.core.counters import registration_karma
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.consts import (
    TEST_FIRSTNAME1,
    TEST_FIRSTNAME2,
    TEST_LASTNAME1,
    TEST_LASTNAME2,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import (
    merge_dicts,
    remove_none_values,
)
from passport.backend.utils.string import smart_text
from six.moves.urllib.parse import urlencode

from .base import BaseTestCase
from .base_test_data import (
    TEST_EMAIL_VALIDATOR_EMAIL,
    TEST_GENERATED_LOGIN,
    TEST_HOST,
    TEST_MAIL_SUBSCRIPTION_SERVICES,
    TEST_ORIGIN,
    TEST_PROFILE_ID,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_SOCIAL_USERID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_IP,
)
from .test_base import (
    build_headers,
    EXISTING_TASK_ID,
)


class BaseAuthSocialRegister(BaseTestCase):
    def setUp(self):
        super(BaseAuthSocialRegister, self).setUp()
        self.patch_build_auth_cookies_and_session()
        self.patch_build_available_social_login()
        self.patch_get_countries_suggest()
        self.patch_get_language_suggest()

        self.track_id = self.env.track_manager.create_test_track(track_type='authorize')
        self.setup_statbox_templates()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.oauth.set_response_value('_token', token_response())
        self.build_auth_cookies_and_session_response.return_value = ([], {})
        self.build_available_social_login_response.return_value = 'uid-11111'

    def tearDown(self):
        del self.track_id
        self.unpatch_build_auth_cookies_and_session()
        self.unpatch_build_available_social_login()
        self.unpatch_get_countries_suggest()
        self.unpatch_get_language_suggest()
        super(BaseAuthSocialRegister, self).tearDown()

    def assert_statbox_ok(
        self,
        firstname=TEST_FIRSTNAME1,
        lastname=TEST_LASTNAME1,
        has_email=True,
        email_confirmed=True,
        unsubscribed_from_maillists=None,
    ):
        lines = [
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='created',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='aliases',
                type=str(ANT['social']),
                operation='added',
                value=TEST_GENERATED_LOGIN,
            ),
        ]

        if has_email:
            now = DatetimeNow(convert_to_datetime=True)
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    bound_at=now,
                    confirmed_at=now,
                    created_at=now,
                    email_id='1',
                    entity='account.emails',
                    new=mask_email_for_statbox(TEST_EMAIL_VALIDATOR_EMAIL),
                    old='-',
                    uid=str(TEST_UID),
                    is_unsafe='1',
                    ip=TEST_USER_IP,
                    operation='added',
                    is_suitable_for_restore='0',
                ),
            )

        if unsubscribed_from_maillists:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.unsubscribed_from_maillists',
                    operation='created',
                    new=unsubscribed_from_maillists,
                    old='-',
                ),
            )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.firstname',
                operation='created',
                new=firstname,
                old='-',
            ),
        )

        if lastname:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.lastname',
                    operation='created',
                    new=lastname,
                    old='-',
                ),
            )

        for entity, operation, new, old in [
            ('person.language', 'created', 'en', '-'),
            ('person.country', 'created', 'en', '-'),
        ]:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    operation=operation,
                    new=new,
                    old=old,
                ),
            )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.fullname',
                operation='created',
                new=firstname + u' ' + lastname if lastname else firstname,
                old='-',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'frodo_karma',
                action='account_register_social',
                login=TEST_GENERATED_LOGIN,
                registration_datetime=DatetimeNow(convert_to_datetime=True),
            ),
        )
        for sid in ['8', '58']:
            lines.append(
                self.env.statbox.entry(
                    'subscriptions',
                    operation='added',
                    sid=sid,
                ),
            )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.display_name',
                operation='created',
                new=u's:123456789:gg:{}{}'.format(firstname, u' ' + lastname if lastname else u''),
                old='-',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'account_created',
                _exclude={'ip', 'is_suggested_login', 'password_quality', 'suggest_generation_number'},
                userid=str(TEST_SOCIAL_USERID),
                track_id=self.track_id,
            ),
        )
        lines.append(self.env.statbox.entry('soc_auth'))
        self.env.statbox.assert_has_written(lines)

    def setup_statbox_templates(self):
        super(BaseAuthSocialRegister, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'soc_auth',
            _inherit_from=['auth'],
            _exclude={'is_suggested_login', 'password_quality', 'suggest_generation_number'},
            mode='social',
            action='auth',
            consumer='dev',
            ip=TEST_USER_IP,
            login=TEST_GENERATED_LOGIN,
            profile_id=str(TEST_PROFILE_ID),
            provider=TEST_PROVIDER['name'],
            track_id=self.track_id,
            uid=str(TEST_UID),
            userid=str(TEST_SOCIAL_USERID),
        )


@with_settings_hosts(
    SENDER_MAIL_SUBSCRIPTION_SERVICES=TEST_MAIL_SUBSCRIPTION_SERVICES,
    **mock_counters()
)
class TestAuthSocialRegister(BaseAuthSocialRegister):
    default_url = '/1/bundle/auth/social/register/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = dict(
        accept_language='ru',
        cookie=TEST_USER_COOKIES,
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        user_ip=TEST_USER_IP,
        x_forwarded_for=True,
    )

    def setUp(self):
        super(TestAuthSocialRegister, self).setUp()
        with self.track_transaction() as track:
            track.retpath = TEST_RETPATH
            track.social_task_data = {
                'profile': {'userid': 100500, 'firstname': TEST_FIRSTNAME1, 'lastname': TEST_LASTNAME1},
                'provider': TEST_PROVIDER,
            }
            track.is_captcha_required = False

        self.http_query_args = {
            'eula_accepted': '1',
            'track_id': self.track_id,
        }

    def setup_track(self, **kwargs):
        defaults = dict(
            retpath=TEST_RETPATH,
            social_task_id=EXISTING_TASK_ID,
            social_task_data=self.build_task(),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])

        with self.track_transaction() as track:
            for key in kwargs:
                setattr(track, key, kwargs[key])

    def build_task(
        self,
        avatar=None,
        is_lastname_optional=False,
        with_email=True,
        with_firstname=True,
        with_lastname=True,
    ):
        provider = TEST_PROVIDER.copy()
        if is_lastname_optional:
            provider['is_lastname_optional'] = True
        task_data = {
            'profile': {
                'userid': TEST_SOCIAL_USERID,
                'links': ['http://yandex.ru'],
                'provider': provider,
            },
            'token': {
                'application_attributes': {
                    'id': 'facebook',
                    'third_party': False,
                },
            },
        }
        if with_email:
            task_data['profile']['email'] = 'user@example.com'
        if with_firstname:
            task_data['profile']['firstname'] = TEST_FIRSTNAME1
        if with_lastname:
            task_data['profile']['lastname'] = TEST_LASTNAME1
        if avatar:
            task_data['profile']['avatar'] = avatar
        return task_data

    def build_ok_response(self, **kwargs):
        profile = self.build_social_profile_response()
        defaults = dict(
            account=self.build_account_response(),
            has_enabled_accounts=True,
            is_native=False,
            profile=profile,
            profile_id=123456789,
            provider=profile.get('provider'),
            retpath=TEST_RETPATH,
            state='auth',
            track_id=self.track_id,
        )
        kwargs = merge_dicts(defaults, kwargs)
        kwargs['provider'] = kwargs.get('profile', dict()).get('provider')
        return remove_none_values(kwargs)

    def build_account_response(self, **kwargs):
        defaults = dict(
            login='uid-11111',
            is_pdd=False,
            display_name=self.build_display_name_response(),
            uid=1,
        )
        return merge_dicts(defaults, kwargs)

    def build_display_name_response(self, name=None):
        display_name = {
            'name': name or (TEST_FIRSTNAME1 + ' ' + TEST_LASTNAME1),
            'social': {
                'profile_id': 123456789,
                'provider': 'gg',
            },
        }
        display_name['name'] = smart_text(display_name['name'])
        return display_name

    def build_social_profile_response(self, **kwargs):
        defaults = dict(
            email='user@example.com',
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            links=['http://yandex.ru'],
            provider=self.build_social_provider_response(),
            userid=100000000,
        )
        kwargs = remove_none_values(merge_dicts(defaults, kwargs))

        if kwargs.get('firstname') is not None:
            kwargs['firstname'] = kwargs['firstname']

        if kwargs.get('lastname') is not None:
            kwargs['lastname'] = kwargs['lastname']

        return kwargs

    def build_social_provider_response(self, **kwargs):
        defaults = dict(
            code='gg',
            id=5,
            name='google',
        )
        return remove_none_values(merge_dicts(defaults, kwargs))

    def assert_db_ok(
        self,
        firstname=TEST_FIRSTNAME1,
        lastname=TEST_LASTNAME1,
        unsubscribed_from_maillists=None,
    ):
        shard_kwargs = dict(uid=1)

        expected_attrs = {
            'person.dont_use_displayname_as_public_name': '1',
        }
        missing_attrs = list()

        if lastname is not None:
            expected_attrs.update({'person.lastname': lastname.encode('utf8')})
        else:
            missing_attrs.append('person.lastname')

        if firstname is not None:
            expected_attrs.update({'person.firstname': firstname.encode('utf8')})
        else:
            missing_attrs.append('person.firstname')

        if unsubscribed_from_maillists:
            expected_attrs.update({'account.unsubscribed_from_maillists': unsubscribed_from_maillists})
        else:
            missing_attrs.append('account.unsubscribed_from_maillists')

        for attr_name, attr_value in expected_attrs.items():
            self.env.db.check_db_attr(
                attr_name=attr_name,
                value=attr_value,
                **shard_kwargs
            )

        for attr_name in missing_attrs:
            self.env.db.check_db_attr_missing(attr_name=attr_name, **shard_kwargs)

    def _check(
        self,
        status,
        eula_accepted='1',
        errors=None,
        with_lastname=True,
        account_has_profiles=False,
        with_email=True,
        is_lastname_optional=False,
        avatar=None,
        headers=None,
        with_check_db=True,
        origin=None,
        unsubscribe_from_maillists=None,
        with_social_task_data=True,
    ):
        social_task_data = None
        if with_social_task_data:
            social_task_data = self.build_task(
                avatar=avatar,
                is_lastname_optional=is_lastname_optional,
                with_email=with_email,
                with_lastname=with_lastname,
            )
        self.setup_track(social_task_data=social_task_data)

        if account_has_profiles:
            api_profiles_response = get_profiles_response()
            uid = api_profiles_response['profiles'][0]['uid']
            blackbox_response = blackbox_userinfo_response(uid=uid)
            self.env.blackbox.set_response_value('userinfo', blackbox_response)
        else:
            api_profiles_response = {'profiles': []}

        api_response = {'profiles': [get_profiles_response()['profiles'][0]]}
        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([
            api_profiles_response,
            bind_api_response,
            api_response,
        ])

        data = {'eula_accepted': eula_accepted, 'track_id': self.track_id}
        if unsubscribe_from_maillists:
            data['unsubscribe_from_maillists'] = True
        if origin is not None:
            data['origin'] = origin
        rv = self.make_request(query_args=data, headers=headers)

        data = json.loads(rv.data)

        if status == 'error':
            eq_(data['status'], 'error')
            eq_(data['errors'], errors)
            return data

        display_name_kwargs = dict()
        if not with_lastname:
            display_name_kwargs.update(name=TEST_FIRSTNAME1)
        display_name_response = self.build_display_name_response(**display_name_kwargs)

        provider_kwargs = dict()
        if is_lastname_optional:
            provider_kwargs.update(is_lastname_optional=True)
        provider_response = self.build_social_provider_response(**provider_kwargs)
        profile_kwargs = dict(
            avatar=avatar,
            provider=provider_response,
        )
        if not with_email:
            profile_kwargs.update(email=None)
        if not with_lastname:
            profile_kwargs.update(lastname=None)
        profile_response = self.build_social_profile_response(**profile_kwargs)

        ok_response = self.build_ok_response(
            account=self.build_account_response(
                display_name=display_name_response,
            ),
            profile=profile_response,
        )
        self.assert_ok_response(rv, **ok_response)

        kwargs = dict(unsubscribed_from_maillists=unsubscribe_from_maillists)
        if not with_lastname:
            kwargs.update(lastname=None)

        if with_check_db:
            self.assert_db_ok(**kwargs)

        return data

    def test_ok(self):
        self._check('ok')
        self.assert_statbox_ok()
        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 1)

    def test_unsubscribe_from_maillists__known_origin__ok(self):
        self._check('ok', origin=TEST_ORIGIN, unsubscribe_from_maillists='1')
        self.assert_statbox_ok(unsubscribed_from_maillists='1')

    def test_unsubscribe_from_maillists__no_origin__ok(self):
        self._check('ok', unsubscribe_from_maillists='all')
        self.assert_statbox_ok(unsubscribed_from_maillists='all')

    def test_unsubscribe_from_maillists__unknown_origin__ok(self):
        self._check('ok', origin='foo', unsubscribe_from_maillists='all')
        self.assert_statbox_ok(unsubscribed_from_maillists='all')

    def test_already_registered(self):
        with self.track_transaction() as track:
            track.is_successful_completed = True
            track.social_register_uid = 1
            track.uid = 1

        account = self.build_account_response()
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=account.get('uid'),
                login=account.get('login'),
                display_name=account.get('display_name'),
            ),
        )
        self._check('ok', with_check_db=False)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('soc_auth'),
            ],
        )

    def test_already_registered__race_no_account(self):
        with self.track_transaction() as track:
            track.is_successful_completed = True
            track.social_register_uid = 1
            track.uid = 1

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self._check('error', errors=['internal.temporary'])
        self.env.statbox.assert_has_written([])

    def test_already_registered__race_no_profile_id(self):
        with self.track_transaction() as track:
            track.is_successful_completed = True
            track.social_register_uid = 1
            track.uid = 1

        account = self.build_account_response()
        if isinstance(account.get('display_name'), dict):
            account = copy(account)
            account['display_name'] = copy(account['display_name'])
            account['display_name'].pop('social', None)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=account.get('uid'),
                login=account.get('login'),
                display_name=account.get('display_name'),
            ),
        )

        self._check('error', errors=['internal.temporary'])
        self.env.statbox.assert_has_written([])

    def test_already_registered_old(self):
        with self.track_transaction() as track:
            track.is_successful_completed = True
        self._check('error', errors=['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_eula_not_accepted(self):
        self._check('error', eula_accepted='0', errors=['eula_accepted.not_accepted'])
        self.env.statbox.assert_has_written([])

    def test_captcha_not_recognized(self):
        with self.track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_recognized = False
        self._check('error', errors=['captcha.required'])
        self.env.statbox.assert_has_written([])

    def test_no_last_name(self):
        data = self._check('error', errors=['name.required'], with_lastname=False)
        eq_(data['profile_link'], 'http://yandex.ru', data)
        self.env.statbox.assert_has_written([])

    def test_account_without_profiles(self):
        self._check('error', errors=['account.already_registered'], account_has_profiles=True)
        self.env.statbox.assert_has_written([])

    def test_email_validation_failed(self):
        self._check('ok')
        self.assert_statbox_ok(email_confirmed=False)

    def test_no_email(self):
        self._check('ok', with_email=False)
        self.assert_statbox_ok(has_email=False, email_confirmed=False)

    def test_no_lastname_optional(self):
        self._check('ok', is_lastname_optional=True, with_lastname=False)
        self.assert_statbox_ok(lastname=False)

    def test_no_already_validated(self):
        self._check('ok')
        self.assert_statbox_ok()

    def test_no_social_task_data(self):
        self._check('error', errors=['task.not_found'], with_social_task_data=False)
        self.env.statbox.assert_has_written([])

    def test_register__wrong_host_header__error(self):
        with self.track_transaction() as track:
            track.social_output_mode = OUTPUT_MODE_SESSIONID

        self._check(
            status='error',
            errors=['host.invalid'],
            headers=dict(host='google.com'),
        )

        self.env.statbox.assert_has_written([])

    def test_with_avatar_ok(self):
        self._check('ok', avatar={'50x0': 'url'})
        self.assert_statbox_ok()
        self.env.avatars_logger.assert_has_written([
            self.env.avatars_logger.entry(
                'base',
                uid='1',
                avatar_to_upload='url',
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip=TEST_USER_IP,
                skip_if_set='0',
            ),
        ])

    def test_with_avatar_invalid_avatar(self):
        self._check('ok', avatar={'abrakadabra': 'url'})
        self.assert_statbox_ok()
        self.env.avatars_logger.assert_has_written([])

    def test_form_firstname_and_lastname(self):
        self.setup_track(
            social_task_data=self.build_task(
                with_firstname=False,
                with_lastname=False,
            ),
        )
        self.env.social_api.set_response_side_effect(
            'get_profiles',
            [
                get_profiles_response(list()),
            ],
        )
        self.env.social_api.set_response_side_effect(
            'bind_task_profile',
            [
                get_bind_response(),
            ],
        )

        rv = self.make_request(
            query_args=dict(
                firstname=TEST_FIRSTNAME2,
                lastname=TEST_LASTNAME2,
            ),
        )

        expected_response = self.build_ok_response(
            account=self.build_account_response(
                display_name=self.build_display_name_response(
                    name=TEST_FIRSTNAME2 + ' ' + TEST_LASTNAME2,
                ),
            ),
            profile=self.build_social_profile_response(
                firstname=None,
                lastname=None,
            ),
        )
        self.assert_ok_response(rv, **expected_response)

        self.assert_db_ok(
            firstname=TEST_FIRSTNAME2,
            lastname=TEST_LASTNAME2,
        )
        self.assert_statbox_ok(
            firstname=TEST_FIRSTNAME2,
            lastname=TEST_LASTNAME2,
        )

    def test_invalid_firstname_and_lastname(self):
        rv = self.make_request(
            query_args=dict(
                firstname=u'f\U0001F2FF',
                lastname=u'l\U0001F2FF',
            ),
        )

        self.assert_error_response(rv, ['firstname.invalid', 'lastname.invalid'])


@with_settings_hosts(
    **mock_counters()
)
class TestAuthSocialRegisterInfo(BaseTestCase):
    def setUp(self):
        super(TestAuthSocialRegisterInfo, self).setUp()
        self.track_id = self.env.track_manager.create_test_track()
        self.env.frodo.set_response_value(u'check', '<spamlist></spamlist>')
        with self.track_transaction() as track:
            track.retpath = TEST_RETPATH
            track.social_return_brief_profile = True
            track.social_place = 'fragment'
            track.social_task_data = {
                'profile': {
                    'userid': 100500,
                    'firstname': TEST_FIRSTNAME1,
                    'lastname': TEST_LASTNAME1,
                    'provider': TEST_PROVIDER,
                },
            }

    def tearDown(self):
        del self.track_id
        super(TestAuthSocialRegisterInfo, self).tearDown()

    def auth_social_create_account_request(self, args, data=None, headers=None):
        return self.env.client.get(
            '/1/bundle/auth/social/register/?consumer=dev&' + urlencode(args),
            data=data,
            headers=headers,
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {'track_id': self.track_id}
        return merge_dicts(base_params, kwargs)

    def build_ok_register_info_response(self):
        return dict(
            is_native=False,
            place='fragment',
            profile=self.build_social_profile_response(),
            provider=TEST_PROVIDER,
            retpath=TEST_RETPATH,
            return_brief_profile=True,
            track_id=self.track_id,
        )

    def build_social_profile_response(self, **kwargs):
        defaults = dict(
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            provider=TEST_PROVIDER,
            userid=100500,
        )
        kwargs = remove_none_values(merge_dicts(defaults, kwargs))

        if kwargs.get('firstname') is not None:
            kwargs['firstname'] = kwargs['firstname']

        if kwargs.get('lastname') is not None:
            kwargs['lastname'] = kwargs['lastname']

        return kwargs

    def test_ok(self):
        rv = self.auth_social_create_account_request(self.query_params(), headers=build_headers())

        self.assert_ok_response(rv, **self.build_ok_register_info_response())
        self.env.statbox.assert_has_written([])

    def test_already_registered(self):
        with self.track_transaction() as track:
            track.is_successful_completed = True
        rv = self.auth_social_create_account_request(self.query_params(), headers=build_headers())
        self.assert_ok_response(rv, **self.build_ok_register_info_response())
        self.env.statbox.assert_has_written([])
