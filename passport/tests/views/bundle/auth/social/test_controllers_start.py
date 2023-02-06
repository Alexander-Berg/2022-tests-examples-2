# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.views.bundle.mixins import CookieCheckStatus
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.utils import (
    check_url_equals,
    with_settings_hosts,
)

from .base import BaseTestCase
from .base_test_data import (
    TEST_APPLICATION,
    TEST_BROKER_CONSUMER,
    TEST_CODE_CHALLENGE,
    TEST_CODE_CHALLENGE_METHOD,
    TEST_HOST,
    TEST_ORIGIN,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_IP,
)


@with_settings_hosts(
    SOCIAL_PROVIDERS_TO_USE_EXTERNAL_USERAGENT=('gg', 'google'),
)
class TestAuthSocialStart(BaseTestCase):
    consumer = 'dev'
    default_url = '/1/bundle/auth/social/start/'
    http_method = 'POST'
    http_query_args = {
        'provider': TEST_PROVIDER['code'],
        'retpath': TEST_RETPATH,
        'application': TEST_APPLICATION,
        'broker_consumer': TEST_BROKER_CONSUMER,
        'frontend_url': 'https://' + TEST_HOST,
    }
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=TEST_USER_COOKIES,
        accept_language='ru',
    )

    def setUp(self):
        super(TestAuthSocialStart, self).setUp()

        self.track_id = self.env.track_manager.create_test_track()
        self.setup_statbox_templates()
        self.patch_check_session_cookie()

        self.patches = []

    def tearDown(self):
        assert self.patches == []
        del self.patches

        self.unpatch_check_session_cookie()
        del self.track_id
        super(TestAuthSocialStart, self).tearDown()

    def test_start__wrong_host_header__error(self):
        rv = self.make_request(headers=dict(host='google.com'))

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'error')
        eq_(data['errors'], ['host.invalid'])
        self.env.statbox.assert_has_written([])

    def test_authorized_status_in_muliauth_context(self):
        self.is_session_valid_response.status = CookieCheckStatus.Valid

        rv = self.make_request()

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'ok', data['status'])
        eq_(data['state'], 'broker.without_auth', data['state'])
        ok_('force_prompt' not in data)

        track = self.track_manager.read(data['track_id'])
        eq_(track.social_output_mode, 'sessionid')
        ok_(not track.oauth_code_challenge)

    def test_with_code_challenge(self):
        """
        Для некоторых провайдеров при передаче параметра code_challenge переключаемся на режим,
        завершающийся выдачей не куки, а оаусного кода подтверждения
        """
        rv = self.make_request(
            query_args=dict(
                provider='google',
                code_challenge=TEST_CODE_CHALLENGE,
                code_challenge_method=TEST_CODE_CHALLENGE_METHOD,
            ),
        )

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'ok', data['status'])
        eq_(data['state'], 'broker.without_auth', data['state'])
        ok_(data['force_prompt'])

        track = self.track_manager.read(data['track_id'])
        eq_(track.social_output_mode, 'authorization_code')
        eq_(track.oauth_code_challenge, TEST_CODE_CHALLENGE)

    def test_other_provider_with_code_challenge(self):
        """
        Если провайдер неподходящий, то передача параметра code_challenge не влияет на процесс
        """
        rv = self.make_request(
            query_args=dict(
                provider='vk',
                code_challenge=TEST_CODE_CHALLENGE,
                code_challenge_method=TEST_CODE_CHALLENGE_METHOD,
            ),
        )

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'ok', data['status'])
        eq_(data['state'], 'broker.without_auth', data['state'])
        ok_('force_prompt' not in data)

        track = self.track_manager.read(data['track_id'])
        eq_(track.social_output_mode, 'sessionid')

    def test_with_old_track_id(self):
        """
        Передадим в параметрах track_id, проверим, что он попал в statbox лог как old_track_id.
        """
        old_track_id = "1" * min(settings.ALLOWED_TRACK_LENGTHS)

        rv = self.make_request(query_args=dict(track_id=old_track_id))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                track_id=data['track_id'],
                old_track_id=old_track_id,
                state='broker.without_auth',
            ),
        ])

    def test_with_process_uuid(self):
        """
        Передадим в параметрах process_uuid, проверим, что он попал в statbox лог.
        """
        process_uuid = 'TEST_PROCESS_UUID'

        self.make_request(query_args=dict(process_uuid=process_uuid))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                process_uuid=process_uuid,
                state='broker.without_auth',
            ),
        ])

    def test_with_origin(self):
        """
        Передадим в параметрах origin, проверим что он попал в statbox лог.
        """
        rv = self.make_request(query_args=dict(origin=TEST_ORIGIN))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                track_id=data['track_id'],
                state='broker.without_auth',
                origin=TEST_ORIGIN,
            ),
        ])

    def test_retpath_in_error_response(self):
        rv = self.make_request(
            query_args=dict(
                code_challenge=TEST_CODE_CHALLENGE,
                code_challenge_method='unknown',
            ),
        )

        self.assert_error_response(
            rv,
            ['code_challenge_method.invalid'],
            retpath=TEST_RETPATH,
        )

    def test_morda_com_retpath(self):
        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/'))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        track = self.track_manager.read(data['track_id'])
        check_url_equals(track.retpath, 'https://www.yandex.com/?redirect=0')

    def test_morda_unicode_retpath(self):
        rv = self.make_request(query_args=dict(retpath=u'https://www.yandex.com/š'))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        track = self.track_manager.read(data['track_id'])
        check_url_equals(track.retpath, u'https://www.yandex.com/š?redirect=0')

    def test_morda_com_retpath_with_query(self):
        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/?%D0%B0=%D1%8F'))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        track = self.track_manager.read(data['track_id'])
        check_url_equals(track.retpath, 'https://www.yandex.com/?%D0%B0=%D1%8F&redirect=0')

    def test_morda_ru_retpath(self):
        rv = self.make_request(query_args=dict(retpath='https://www.yandex.ru/'))

        data = json.loads(rv.data)
        track_id = data['track_id']

        self.assert_ok_response(
            rv,
            track_id=track_id,
            state='broker.without_auth',
        )

        track = self.track_manager.read(data['track_id'])
        check_url_equals(track.retpath, 'https://www.yandex.ru/')

    def test_morda_com_retpath_error_response(self):
        rv = self.make_request(
            query_args=dict(
                retpath='https://www.yandex.com/',
                code_challenge=TEST_CODE_CHALLENGE,
                code_challenge_method='unknown',
            ),
        )

        self.assert_error_response(
            rv,
            ['code_challenge_method.invalid'],
            retpath='https://www.yandex.com/?redirect=0',
        )

    def test_broker_consumer(self):
        rv = self.make_request(
            query_args=dict(
                broker_consumer=TEST_BROKER_CONSUMER,
            ),
        )

        self.assert_ok_response(rv, check_all=False)

        track = self.track_manager.read(self.track_id)
        eq_(track.social_broker_consumer, TEST_BROKER_CONSUMER)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                broker_consumer=TEST_BROKER_CONSUMER,
                state='broker.without_auth',
            ),
        ])

    @parameterized.expand(
        [
            ('yandextaxi://am/sociallogin',),
            ('yandextaxi://',),
            ('yandextaxi:',),
        ],
    )
    def test_ok_scheme_retpath(self, retpath):
        rv = self.make_request(query_args=dict(retpath=retpath))
        self.assert_ok_response(rv, track_id=self.track_id, state='broker.without_auth')

    def test_device_params(self):
        device_params = dict(
            device_id='device_id',
            device_name='device_name',
            ifv='ifv',
        )

        rv = self.make_request(query_args=device_params)

        self.assert_ok_response(rv, state='broker.without_auth', track_id=self.track_id)

        track = self.track_manager.read(self.track_id)
        assert track.device_id == device_params['device_id']
        assert track.device_ifv == device_params['ifv']
        assert track.device_name == device_params['device_name']
