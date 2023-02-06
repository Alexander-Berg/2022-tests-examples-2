# -*- coding: utf-8 -*-

from copy import deepcopy
import json

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_lrandoms_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_successful_response,
    token_error_response,
    token_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_profiles_response,
    task_data_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.geobase.faker.fake_geobase import FakeRegion
from passport.backend.core.models.phones.faker.phones import build_phone_secured
from passport.backend.core.test.consts import TEST_YANDEX_EMAIL1
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from six.moves.urllib.parse import (
    parse_qs,
    urlencode,
    urlparse,
)

from .base import BaseTestCase
from .base_test_data import (
    TEST_ACCESS_TOKEN,
    TEST_AUTHORIZATION_CODE,
    TEST_AVATAR_URL,
    TEST_BROKER_CONSUMER,
    TEST_CODE_CHALLENGE,
    TEST_DISPLAY_NAME,
    TEST_GENERATED_LOGIN,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_PROFILE_ID,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_RETPATH_NONSTANDARD_SCHEME,
    TEST_SERVICE,
    TEST_SERVICE_SID,
    TEST_SOCIAL_UID,
    TEST_TASK_ID,
    TEST_UID,
    TEST_USER_IP,
    TEST_USER_LOGIN,
    TEST_USERID,
    TEST_YANDEXUID_COOKIE,
)
from .test_base import build_headers
from .utils import create_frodo_params


TEST_ACCOUNT_RESPONSE = {
    'display_name': dict(
        default_avatar='',
        **TEST_DISPLAY_NAME
    ),
    'uid': TEST_SOCIAL_UID,
    'is_yandexoid': False,
    'is_workspace_user': False,
    'display_login': TEST_LITE_LOGIN,
    'person': {
        'firstname': u'\\u0414',
        'language': 'ru',
        'gender': 1,
        'birthday': '1963-05-15',
        'lastname': u'\\u0424',
        'country': 'ru',
    },
    'is_2fa_enabled': False,
    'is_rfc_2fa_enabled': False,
    'login': TEST_LITE_LOGIN,
}


@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestSocialIntegrationalBase(BaseTestCase):
    def prepare_testone_address_response(self, address='test@yandex.ru', native=True):
        response = {
            'users': [
                {
                    'address-list': [
                        {
                            'address': address,
                            'born-date': '2014-12-26 16:11:15',
                            'default': True,
                            'native': native,
                            'prohibit-restore': False,
                            'rpop': False,
                            'silent': False,
                            'unsafe': False,
                            'validated': True,
                        },
                    ],
                    'have_hint': False,
                    'have_password': True,
                    'id': str(TEST_UID),
                    'karma': {
                        'value': 0,
                    },
                    'karma_status': {
                        'value': 0,
                    },
                    'login': TEST_USER_LOGIN,
                    'uid': {
                        'hosted': False,
                        'lite': False,
                        'value': str(TEST_UID),
                    },
                },
            ],
        }
        return json.dumps(response)

    def setUp(self):
        super(TestSocialIntegrationalBase, self).setUp()

        self.patch_build_available_social_login()
        self.patch_get_countries_suggest()
        self.patch_get_language_suggest()
        self.patch_registration_captcha_required()

        self.patches = []

        self.track_id = self.env.track_manager.create_test_track(track_type='authorize')

        self.setup_statbox_templates()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.prepare_testone_address_response(native=False),
        )

        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code=TEST_AUTHORIZATION_CODE),
        )

        createsession_response = blackbox_createsession_response()
        self.env.blackbox.set_blackbox_response_value('createsession', createsession_response)
        lrandoms_response = blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        self.env.blackbox.set_response_side_effect(
            'sign',
            [
                blackbox_sign_response(),
                blackbox_sign_response(),
            ],
        )

        self.build_available_social_login_response.return_value = TEST_GENERATED_LOGIN

        self.fake_region = FakeRegion()
        self.fake_region.start()

        self.fake_region.set_region_for_ip(
            TEST_USER_IP,
            dict(
                country=dict(id=1, short_en_name='ru'),
                timezone='Europe/Moscow'
            ),
        )

    def tearDown(self):
        self.fake_region.stop()
        self.unpatch_registration_captcha_required()
        self.unpatch_get_language_suggest()
        self.unpatch_get_countries_suggest()
        self.unpatch_build_available_social_login()

        assert self.patches == []
        del self.patches

        del self.track_id
        super(TestSocialIntegrationalBase, self).tearDown()

    def patch_registration_captcha_required(self):
        self.is_captcha_required = Mock(return_value=False)
        self.patch_for_registration_captcha_required = patch(
            'passport.backend.api.views.bundle.auth.social.base.social_registration_captcha.is_required',
            self.is_captcha_required,
        )
        self.patch_for_registration_captcha_required.start()

    def unpatch_registration_captcha_required(self):
        self.patch_for_registration_captcha_required.stop()
        del self.patch_for_registration_captcha_required
        del self.is_captcha_required

    def make_api_request(self, action, args=None, data=None, headers=None, method='post', cookie=None):
        url = '/1/bundle/auth/social/%s/?consumer=dev' % action
        if args:
            url = '%s&%s' % (url, urlencode(args))
        _headers = build_headers(cookie=cookie)
        if headers:
            _headers.update(headers)

        exec_method = getattr(self.env.client, method)

        return exec_method(
            url,
            data=data,
            headers=_headers,
        )

    def _get_blackbox_responses(self, profiles_data, account_enabled=True, password_changing_required=False, **bb_kwargs):
        dbfields = {}
        attributes = {}

        if password_changing_required:
            dbfields['subscription.login_rule.8'] = 4
            attributes['password.forced_changing_reason'] = '1'

        accounts_to_login_with_profile = []
        for profile in profiles_data['profiles']:
            if profile['allow_auth']:
                bb_params = dict(
                    uid=profile['uid'],
                    login=TEST_LOGIN,
                    display_name=TEST_DISPLAY_NAME,
                    enabled=account_enabled,
                    dbfields=dbfields,
                    attributes=attributes,
                )
                bb_params.update(bb_kwargs)
                bb_params = deep_merge(bb_params, build_phone_secured(1, TEST_PHONE_NUMBER.e164))
                accounts_to_login_with_profile.append(bb_params)

        responses = list()

        if accounts_to_login_with_profile:
            responses.append(blackbox_userinfo_response_multiple(accounts_to_login_with_profile))

        suggested_account_by_email = blackbox_userinfo_response(uid=None)
        responses.append(suggested_account_by_email)

        responses.append(self.prepare_testone_address_response(native=False))

        return responses

    def mock_native_start_externals(self, profiles_count, account_enabled=True, bb_kwargs=None,
                                    oauth_error=None, oauth_error_description=None):

        # Ответ social-broker.
        task_data = self.get_task_by_token_response()
        self.env.social_broker.set_social_broker_response_value(task_data)

        # Ответ OAuth
        if oauth_error is None:
            oauth_response = token_response(access_token=TEST_ACCESS_TOKEN)
        else:
            oauth_response = token_error_response(error=oauth_error, error_description=oauth_error_description)
        self.env.oauth.set_response_value('_token', oauth_response)

        profiles_data = get_profiles_response()
        new_profiles_data = {'profiles': profiles_data['profiles'][:profiles_count]}
        bind_api_response = get_bind_response()

        self.env.social_api.set_social_api_response_side_effect([new_profiles_data, bind_api_response])

        blackbox_response = self._get_blackbox_responses(
            new_profiles_data,
            account_enabled=account_enabled,
            **(bb_kwargs or {})
        )
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_response)

        self.task_data = task_data
        self.profiles_count = profiles_count

    def mock_callback_externals(
        self,
        profiles_count,
        account_enabled=True,
        bb_kwargs=None,
        with_social_api_get_task_data_request=True,
    ):
        task_data = self.get_task_data_response()
        profiles_data = get_profiles_response()
        new_profiles_data = {'profiles': profiles_data['profiles'][:profiles_count]}
        bind_api_response = get_bind_response()

        social_api_responses = list()
        if with_social_api_get_task_data_request:
            social_api_responses.append(task_data)
        social_api_responses.extend([new_profiles_data, bind_api_response])
        self.env.social_api.set_social_api_response_side_effect(social_api_responses)

        blackbox_response = self._get_blackbox_responses(
            new_profiles_data,
            account_enabled=account_enabled,
            **(bb_kwargs or {})
        )
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_response)

        self.task_data = task_data
        self.profiles_count = profiles_count

    def mock_choose_externals(self, api_response_item, account_enabled=True, password_changing_required=False,
                              bb_kwargs=None):
        if api_response_item is not None:
            api_response = get_profiles_response()
            uid = api_response['profiles'][api_response_item]['uid']

            dbfields = {}
            attributes = {}
            if password_changing_required:
                dbfields['subscription.login_rule.8'] = 4
                attributes['password.forced_changing_reason'] = '1'

            blackbox_response = blackbox_userinfo_response(
                **merge_dicts(
                    dict(
                        uid=uid,
                        enabled=account_enabled,
                        login=TEST_USER_LOGIN,
                        display_name=TEST_DISPLAY_NAME,
                        dbfields=dbfields,
                        **deep_merge(dict(attributes=attributes), build_phone_secured(1, TEST_PHONE_NUMBER.e164))
                    ),
                    bb_kwargs or {},
                )
            )
            self.env.blackbox.set_blackbox_response_side_effect(
                'userinfo',
                [
                    blackbox_response,
                    self.prepare_testone_address_response(native=False),
                ],
            )
        else:
            api_response = {'profiles': []}
            uid = TEST_SOCIAL_UID

        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([api_response, bind_api_response])

        return uid

    def mock_register_externals(self, account_has_profiles=False, captcha_raised=False):
        if captcha_raised:
            self.is_captcha_required.return_value = captcha_raised

        if account_has_profiles:
            api_profiles_response = get_profiles_response()
            uid = api_profiles_response['profiles'][0]['uid']
            blackbox_response = blackbox_userinfo_response(uid=uid)
            self.env.blackbox.set_blackbox_response_side_effect(
                'userinfo',
                [
                    blackbox_response,
                    self.prepare_testone_address_response(native=False),
                ],
            )
        else:
            api_profiles_response = {'profiles': []}
            self.env.blackbox.set_blackbox_response_value(
                'userinfo',
                self.prepare_testone_address_response(native=False),
            )

        api_response = {'profiles': [get_profiles_response()['profiles'][0]]}
        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([api_profiles_response, bind_api_response, api_response])

    def assert_blackbox_createsesion_call(self, profile_id):
        for call in self.env.blackbox._mock.request.call_args_list:
            url = call[0][1]
            qs = parse_qs(urlparse(url).query)
            if qs.get('method') != ['createsession']:
                continue
            expected = {
                'have_password': ['0'],
                'social_id': [str(profile_id)],
            }

            self.assertDictContainsSubset(expected, qs)
            return

        raise AssertionError('Blackbox createsession method was not called')

    def assert_auth_response(self, response, check_frodo=False, check_subscription=False,
                             registered=False,
                             is_xtoken_response=False, is_auth_code_response=False, check_createsession=True,
                             nonstandard_scheme=False, with_lah_cookie=True):
        eq_(response.status_code, 200, response.data)
        data = json.loads(response.data)

        eq_(data['status'], 'ok')
        eq_(data['state'], 'auth', data['state'])
        eq_(data['profile_id'], TEST_PROFILE_ID, data['profile_id'])

        eq_(data['provider'], TEST_PROVIDER, data['provider'])
        eq_(data['is_native'], is_xtoken_response)

        account = data['account']
        self.uid = account['uid']
        self.login = account['login']

        if is_xtoken_response:
            self.track_id = data['track_id']
            ok_(len(self.env.oauth.requests) > 0)
            eq_(data['x_token'], TEST_ACCESS_TOKEN)
        elif is_auth_code_response:
            self.track_id = data['track_id']
            ok_(len(self.env.oauth.requests) > 0)
            self.env.oauth.requests[0].assert_post_data_contains({
                'code_challenge': TEST_CODE_CHALLENGE,
                'code_challenge_method': 'S256',
                'by_uid': '1',
                'uid': str(self.uid),
            })
            eq_(data['yandex_authorization_code'], TEST_AUTHORIZATION_CODE)
        else:
            if check_createsession:
                self.assert_blackbox_createsesion_call(TEST_PROFILE_ID)

            cookies = sorted(data['cookies'])

            if with_lah_cookie:
                (
                    l_cookie, sessionid_cookie, lah_cookie, mda2_beacon_cookie,
                    sessionid2_cookie, yandexlogin_cookie, yp_cookie, ys_cookie,
                ) = cookies
                self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
            else:
                (
                    l_cookie, sessionid_cookie, mda2_beacon_cookie,
                    sessionid2_cookie, yandexlogin_cookie, yp_cookie, ys_cookie,
                ) = cookies

            self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
            self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
            self.assert_cookie_ok(l_cookie, 'L')
            self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
            self.assert_cookie_ok(yp_cookie, 'yp')
            self.assert_cookie_ok(mda2_beacon_cookie, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        # После регистрации в display_name пропишется новый profile_id
        expected_display_name = deepcopy(TEST_DISPLAY_NAME)
        if registered:
            expected_display_name['social']['profile_id'] = TEST_PROFILE_ID

        self.assertDictEqual(account['display_name'], expected_display_name)

        if check_subscription:
            self.env.db.check('attributes', 'subscription.%s' % TEST_SERVICE_SID, '1', uid=self.uid, db='passportdbshard1')

        if check_frodo:
            args = {
                'uid': str(self.uid),
                'login': self.login,
                'fname': 'Lastname',
                'iname': 'Firstname',
            }
            if check_subscription:
                args['from'] = TEST_SERVICE
            self.check_frodo_call(**args)

        track = self.track_manager.read(self.track_id)
        eq_(track.is_successful_completed, True)
        eq_(track.is_password_passed, False)
        eq_(track.have_password, False)
        eq_(track.social_output_mode == 'xtoken', is_xtoken_response)
        eq_(track.social_output_mode == 'authorization_code', is_auth_code_response)
        eq_(track.auth_method, 'social_%(code)s' % TEST_PROVIDER)

        # Эти поля проставляются либо в /start, либо в /native_start, поэтому проверим их здесь еще раз
        if nonstandard_scheme:
            eq_(track.retpath, TEST_RETPATH_NONSTANDARD_SCHEME)
        else:
            eq_(track.retpath, TEST_RETPATH)
        eq_(track.track_type, 'authorize')
        eq_(track.social_return_brief_profile, False)

        expected_phone_log_values = []

        # У только что зарегистрированного пользователя нет телефона.
        if not registered:
            expected_phone_log_values = [
                self.env.phone_logger.get_log_entry(
                    TEST_SOCIAL_UID,
                    TEST_PHONE_NUMBER.e164,
                    TEST_YANDEXUID_COOKIE,
                ),
            ]

        self.env.phone_logger.assert_has_written(expected_phone_log_values)
        self.env.phone_logger.clear_entries()

        return data

    def assert_force_complete_lite_response(self, response, has_recovery_method=False, is_native=False):
        expected_response = dict(
            state='force_complete_lite',
            has_recovery_method=has_recovery_method,
            account=TEST_ACCOUNT_RESPONSE,
            has_enabled_accounts=True,
            track_id=self.track_id,
            return_brief_profile=False,
            retpath=TEST_RETPATH,
            place='query',
            provider=TEST_PROVIDER,
            is_native=is_native,
            profile=dict(**self.task_data['profile']),
            broker_consumer=TEST_BROKER_CONSUMER,
        )
        self.assert_ok_response(response, **expected_response)
        eq_(self.env.blackbox.get_requests_by_method('createsession'), [])
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_successful_completed)

    def assert_start_response(self, response):
        eq_(response.status_code, 200, response.data)
        data = json.loads(response.data)

        eq_(data['status'], 'ok')
        eq_(data['state'], 'broker.without_auth', data['state'])
        track_id = data.get('track_id')
        ok_(track_id)
        self.track_id = track_id

        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.track_type, 'authorize')
        eq_(track.social_return_brief_profile, False)
        eq_(bool(track.is_successful_completed), False)
        return data

    def assert_choose_response(self, response, is_xtoken_response=False, is_auth_code_response=False):

        eq_(response.status_code, 200, response.data)
        data = json.loads(response.data)

        if is_xtoken_response:
            self.track_id = data['track_id']

        eq_(data['status'], 'ok')
        eq_(data['state'], 'choose', data['state'])

        self.assertDictEqual(data['profile'], self.task_data['profile'])
        eq_(data['retpath'], TEST_RETPATH)
        ok_('track_id' in data)
        eq_(data['has_enabled_accounts'], True)
        eq_(data['place'], 'query')
        eq_(data['provider'], TEST_PROVIDER)
        eq_(data['is_native'], is_xtoken_response)

        accounts = data['accounts']

        expected_accounts_count = min(self.profiles_count, 2)
        eq_(len(accounts), expected_accounts_count)

        self.assertDictEqual(accounts[0]['display_name'], TEST_DISPLAY_NAME)

        track = self.track_manager.read(self.track_id)
        eq_(bool(track.is_successful_completed), False)
        ok_(track.social_task_data)
        eq_(track.social_task_id, TEST_TASK_ID)
        eq_(track.social_output_mode == 'xtoken', is_xtoken_response)
        eq_(track.social_output_mode == 'authorization_code', is_auth_code_response)
        return data

    def assert_register_response(self, response, is_xtoken_response=False, is_auth_code_response=False):
        eq_(response.status_code, 200, response.data)
        data = json.loads(response.data)

        if is_xtoken_response or is_auth_code_response:
            self.track_id = data['track_id']

        eq_(data['status'], 'ok')
        eq_(data['state'], 'register', data['state'])

        self.assertDictEqual(data['profile'], self.task_data['profile'])
        eq_(data['retpath'], TEST_RETPATH)
        ok_('track_id' in data)
        eq_(data['has_enabled_accounts'], False)
        eq_(data['place'], 'query')
        eq_(data['provider'], TEST_PROVIDER)
        eq_(data['is_native'], is_xtoken_response)

        track = self.track_manager.read(self.track_id)

        eq_(track.social_task_id, TEST_TASK_ID)
        eq_(bool(track.is_successful_completed), False)
        ok_(track.social_task_data)
        eq_(track.social_output_mode == 'xtoken', is_xtoken_response)
        eq_(track.social_output_mode == 'authorization_code', is_auth_code_response)
        return data

    def assert_error_response(self, response, errors, is_native=False):
        eq_(response.status_code, 200, response.data)
        data = json.loads(response.data)

        eq_(data['status'], 'error')
        eq_(data['errors'], errors)

        eq_(data.get('is_native', False), is_native)

        track_id = json.loads(response.data).get('track_id')
        if track_id:
            track = self.track_manager.read(track_id)
            eq_(track.social_output_mode == 'xtoken', is_native)

        return data

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        frodo_args = create_frodo_params(**kwargs)
        frodo_args['v2_account_country'] = 'en'
        frodo_args['v2_account_language'] = 'en'
        requests[0].assert_query_equals(frodo_args)

    def assert_records__start_and_reset(self, with_service=False, origin=None):
        additional_kwargs = {}
        if with_service:
            additional_kwargs['from'] = TEST_SERVICE
        if origin:
            additional_kwargs['origin'] = origin
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                state='broker.without_auth',
                track_id=self.track_id,
                **additional_kwargs
            ),
        ])
        self.env.statbox_handle_mock.reset_mock()

        self.assert_events_are_empty(self.env.handle_mock)

    def assert_records_callback_and_reset(
        self,
        state,
        end=True,
        auth=False,
        uids=None,
        enabled_count=0,
        with_service=True,
        uids_count='1',
        session_method='create',
        old_session_uids=None,
        cookie_set=True,
        with_check_cookies=False
    ):
        cookie_kwargs = {}
        if with_service:
            cookie_kwargs['from'] = TEST_SERVICE
        if old_session_uids:
            cookie_kwargs['old_session_uids'] = old_session_uids
        callback_end_kwargs = {}
        disabled_accounts_count = 0
        if uids:
            disabled_accounts_count = len(uids) - enabled_count
            callback_end_kwargs['accounts'] = ','.join(map(str, uids))
        callback_end_kwargs['disabled_accounts_count'] = str(disabled_accounts_count)
        lines = [self.env.statbox.entry('callback_begin', track_id=self.track_id)]
        if end:
            lines.append(
                self.env.statbox.entry(
                    'callback_end',
                    track_id=self.track_id,
                    state=state,
                    enabled_accounts_count=str(enabled_count),
                    **callback_end_kwargs
                ),
            )

        if auth:
            lines += [
                self.env.statbox.entry(
                    'auth',
                    track_id=self.track_id,
                ),
            ]
            if with_check_cookies:
                lines.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
            if cookie_set:
                lines += [
                    self.env.statbox.entry(
                        'cookie_set',
                        mode='any_auth',
                        track_id=self.track_id,
                        uid=str(TEST_SOCIAL_UID),
                        input_login=self.login,
                        session_method=session_method,
                        uids_count=uids_count,
                        person_country='ru',
                        **cookie_kwargs
                    ),
                ]
        elif with_check_cookies:
            lines.append(self.env.statbox.entry('check_cookies'))
        if with_service:
            lines.append(
                self.env.statbox.entry(
                    'subscriptions',
                    uid=str(TEST_SOCIAL_UID),
                    consumer='-',
                    sid=str(TEST_SERVICE_SID),
                ),
            )

        self.env.statbox.assert_has_written(lines)
        self.env.statbox_handle_mock.reset_mock()

        historydb_entries = {}
        if with_service:
            historydb_entries.update({
                'sid.add': str(TEST_SERVICE_SID),
                'action': 'subscribe',
                'from': TEST_SERVICE,
                'user_agent': 'curl',
            })
        self.assert_events_are_logged(self.env.handle_mock, historydb_entries)
        self.env.handle_mock.reset_mock()

    def assert_records_native_start_and_reset(self, state, end=True, auth=False, uids=None, enabled_count=0,
                                              nonstandard_scheme=False, origin=None, cookie_set=True):
        sub_kwargs = {}
        if origin:
            sub_kwargs['origin'] = origin
        lines = [
            self.env.statbox.entry(
                'submitted',
                _exclude=['broker_consumer', 'application'],
                type='social_native',
                track_id=self.track_id,
                retpath=TEST_RETPATH_NONSTANDARD_SCHEME if nonstandard_scheme else TEST_RETPATH,
                **sub_kwargs
            ),
        ]
        if end:
            lines.append(
                self.env.statbox.entry(
                    'callback_end',
                    track_id=self.track_id,
                    state=state,
                    disabled_accounts_count=str(len(uids) - enabled_count),
                    enabled_accounts_count=str(enabled_count),
                    accounts=','.join(map(str, uids)),
                ),
            )

        if auth:
            lines.append(
                self.env.statbox.entry(
                    'auth',
                    track_id=self.track_id,
                ),
            )
            if cookie_set:
                lines.append(
                    self.env.statbox.entry(
                        'cookie_set',
                        track_id=self.track_id,
                        uid=TEST_SOCIAL_UID,
                        input_login=self.login,
                        uids_count='1',
                        person_country='ru',
                    ),
                )

        self.env.statbox.assert_has_written(lines)
        self.env.statbox_handle_mock.reset_mock()

        self.assert_events_are_empty(self.env.handle_mock)

    def assert_records_choose_and_reset(self, with_service=True, uid=TEST_UID, login=TEST_LOGIN,
                                        uids_count='1', session_method='create', old_session_uids=None,
                                        with_multibrowser=True, with_check_cookies=False):
        cookie_kwargs = {}
        if with_service:
            cookie_kwargs['from'] = TEST_SERVICE
        if old_session_uids:
            cookie_kwargs['old_session_uids'] = old_session_uids
        lines = [
            self.env.statbox.entry(
                'auth',
                uid=str(uid),
                track_id=self.track_id,
                login=login,
            ),
        ]
        if with_check_cookies:
            lines.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
        lines.append(self.env.statbox.entry(
                'cookie_set',
                mode='any_auth',
                track_id=self.track_id,
                uid=str(uid),
                input_login=self.login,
                uids_count=uids_count,
                person_country='ru',
                session_method=session_method,
                **cookie_kwargs
            )
        )
        if with_multibrowser:
            lines.append(
                self.env.statbox.entry(
                    'multibrowser_set',
                    uid=str(uid),
                ),
            )
        if with_service:
            lines.append(
                self.env.statbox.entry(
                    'subscriptions',
                    uid=str(uid),
                    consumer='-',
                    sid=str(TEST_SERVICE_SID),
                ),
            )

        self.env.statbox.assert_has_written(lines)
        self.env.statbox_handle_mock.reset_mock()

        historydb_entries = {}
        if with_service:
            historydb_entries.update({
                'sid.add': str(TEST_SERVICE_SID),
                'action': 'subscribe',
                'from': TEST_SERVICE,
                'user_agent': 'curl',
            })
        self.assert_events_are_logged(self.env.handle_mock, historydb_entries)
        self.env.handle_mock.reset_mock()

    def assert_records_register_and_reset(self, with_service=True, captcha_passed=False,
                                          uids_count='1', session_method='create', old_session_uids=None,
                                          with_multibrowser=True, ttl=5, with_check_cookies=False):
        cookie_kwargs = {
            'ttl': str(ttl),
        }
        if old_session_uids:
            cookie_kwargs.update(old_session_uids=old_session_uids)
        if with_service:
            cookie_kwargs['from'] = TEST_SERVICE
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

        now = DatetimeNow(convert_to_datetime=True)
        lines.append(
            self.env.statbox.entry(
                'account_modification',
                bound_at=now,
                confirmed_at=now,
                created_at=now,
                email_id='1',
                entity='account.emails',
                old='-',
                new=mask_email_for_statbox(TEST_YANDEX_EMAIL1),
                uid=str(TEST_UID),
                is_unsafe='1',
                ip=TEST_USER_IP,
                operation='added',
                is_suitable_for_restore='0',
            ),
        )

        for entity, new in [
            ('person.firstname', 'Firstname'),
            ('person.lastname', 'Lastname'),
            ('person.language', 'en'),
            ('person.country', 'en'),
            ('person.gender', 'm'),
            ('person.birthday', '1963-12-28'),
            ('person.fullname', 'Firstname Lastname'),
        ]:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    operation='created',
                    new=new,
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
                    sid=sid,
                ),
            )

        display_name = DisplayName(TEST_DISPLAY_NAME['name'], TEST_PROVIDER['code'], TEST_PROFILE_ID)

        lines.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='person.display_name',
                operation='created',
                new=str(display_name),
                old='-',
            ),
            self.env.statbox.entry(
                'account_created',
                _exclude={'ip', 'is_suggested_login', 'password_quality', 'suggest_generation_number'},
                userid=str(TEST_USERID),
                track_id=self.track_id,
            ),
            self.env.statbox.entry(
                'auth',
                uid=str(TEST_UID),
                userid=TEST_USERID,
                track_id=self.track_id,
                provider=TEST_PROVIDER['name'],
                login=TEST_GENERATED_LOGIN,
            ),
        ])
        if with_check_cookies:
            lines.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
        lines.append(self.env.statbox.entry(
                'cookie_set',
                mode='any_auth',
                track_id=self.track_id,
                uid=str(TEST_UID),
                input_login=self.login,
                captcha_passed='1' if captcha_passed else '0',
                session_method=session_method,
                uids_count=uids_count,
                person_country='en',
                retpath=TEST_RETPATH,
                **cookie_kwargs
            )
        )

        if with_multibrowser:
            lines.append(
                self.env.statbox.entry('multibrowser_set'),
            )
        if with_service:
            lines.append(
                self.env.statbox.entry(
                    'subscriptions',
                    consumer='-',
                    sid=str(TEST_SERVICE_SID),
                ),
            )

        self.env.statbox.assert_has_written(lines)
        self.env.avatars_logger.assert_has_written([
            self.env.avatars_logger.entry(
                'base',
                uid='1',
                avatar_to_upload=TEST_AVATAR_URL,
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip=TEST_USER_IP,
                skip_if_set='0',
            ),
        ])
        self.env.statbox_handle_mock.reset_mock()

        now = TimeNow()

        historydb_entries = [
            {'name': 'info.login', 'value': TEST_GENERATED_LOGIN},
            {'name': 'info.ena', 'value': '1'},
            {'name': 'info.disabled_status', 'value': '0'},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
            {'name': 'info.firstname', 'value': 'Firstname'},
            {'name': 'info.lastname', 'value': 'Lastname'},
            {'name': 'info.sex', 'value': '1'},
            {'name': 'info.birthday', 'value': '1963-12-28'},
            {'name': 'info.country', 'value': 'en'},
            {'name': 'info.tz', 'value': 'Europe/Moscow'},
            {'name': 'info.lang', 'value': 'en'},
            {'name': 'info.karma_prefix', 'value': '0'},
            {'name': 'info.karma_full', 'value': '0'},
            {'name': 'info.karma', 'value': '0'},
            {'name': 'alias.social.add', 'value': TEST_GENERATED_LOGIN},
            {'name': 'sid.add', 'value': '8|{0},58|{0}'.format(TEST_GENERATED_LOGIN)},
            {'name': 'email.1', 'value': 'created'},
            {'name': 'email.1.address', 'value': TEST_YANDEX_EMAIL1},
            {'name': 'email.1.confirmed_at', 'value': now},
            {'name': 'email.1.created_at', 'value': now},
            {'name': 'email.1.bound_at', 'value': now},
            {'name': 'email.1.is_unsafe', 'value': '1'},
            {'name': 'action', 'value': 'account_register_social'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
            {'name': 'info.display_name', 'value': 's:123456789:gg:Firstname Lastname'},
            {'name': 'info.dont_use_displayname_as_public_name', 'value': '1'},
            {'name': 'action', 'value': 'change_display_name'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        ]

        if with_service:
            historydb_entries += [
                {'name': 'sid.add', 'value': str(TEST_SERVICE_SID)},
                {'name': 'action', 'value': 'subscribe'},
                {'name': 'from', 'value': TEST_SERVICE},
                {'name': 'user_agent', 'value': 'curl'},
            ]
        self.assert_events_are_logged_with_order(self.env.handle_mock, historydb_entries)
        self.env.handle_mock.reset_mock()

        centraldb_queries = 3
        sharddb_queries = 5 if with_service else 4

        eq_(
            self.env.db.query_count('passportdbcentral'),
            centraldb_queries,
        )
        eq_(
            self.env.db.query_count('passportdbshard1'),
            sharddb_queries,
        )
        missing_attributes = [
            'account.is_disabled',
            'person.city',
            'karma.value',
            'password.quality',
            'password.update_datetime',
            'password.encrypted',
            'person.timezone',
        ]

        present_attributes = {
            'account.registration_datetime': TimeNow(),
            'person.firstname': 'Firstname',
            'person.lastname': 'Lastname',
            'account.display_name': str(display_name),
            'person.gender': 'm',
            'person.birthday': '1963-12-28',
            'person.country': 'en',
            'person.language': 'en',
        }

        if with_service:
            present_attributes['subscription.23'] = '1'
        else:
            missing_attributes.append('subscription.23')

        for attribute_name, expected_value in present_attributes.items():
            self.env.db.check('attributes', attribute_name, expected_value, uid=1, db='passportdbshard1')

        for attribute_name in missing_attributes:
            self.env.db.check_missing('attributes', attribute_name, uid=1, db='passportdbshard1')

    def get_task_by_token_response(self):
        return self.env.social_broker.get_task_by_token_response(birthday='1963-12-28')

    def get_task_data_response(self):
        return task_data_response(
            birthday='1963-12-28',
            email=TEST_YANDEX_EMAIL1,
        )
