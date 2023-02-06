# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    assert_false,
    assert_is_none,
    assert_true,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.constants import CHANGE_PASSWORD_REASON_HACKED
from passport.backend.core.builders import captcha
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_params_equal
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
    captcha_voice_response_generate,
)
from passport.backend.core.counters import registration_karma
from passport.backend.core.counters.change_password_counter import get_per_user_ip_buckets
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_IP = '123.123.123.123'
TEST_UID = '111'


class BaseTestCaptcha(BaseTestViews):
    def setUp(self, track_type='register'):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'captcha': ['*'], 'track': ['update']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type_to_create=track_type)
        self.check_url = '/1/captcha/check/?consumer=dev&answer=a&key=b&track_id=' + self.track_id
        self.generate_url = '/1/captcha/generate/?display_language=ru&consumer=dev&track_id=' + self.track_id
        self.generate_url_with_country = '/1/captcha/generate/?country=ru&consumer=dev&track_id=' + self.track_id
        self.generate_url_with_type_country = '/1/captcha/generate/?country={country}&type={type}&consumer=dev&track_id=' + self.track_id
        self.generate_url_with_type_language = '/1/captcha/generate/?display_language={language}&type={type}&consumer=dev&track_id=' + self.track_id

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'captcha_generated',
            track_id=self.track_id,
            mode='captcha_generate',
            key='1p',
            image_type='lite',
        )
        self.env.statbox.bind_entry(
            'captcha_used_cached',
            track_id=self.track_id,
            mode='captcha_generate',
            key='1p',
            cached='1',
        )
        self.env.statbox.bind_entry(
            'captcha_checked',
            track_id=self.track_id,
            mode='captcha_check',
            action='captcha_check',
            key='b',
            is_recognized='1',
            reason='check',
        )
        self.env.statbox.bind_entry(
            'bad_reg_karma',
            track_id=self.track_id,
            action='captcha_check',
            onliner_status='blocked_black',
        )
        self.env.statbox.bind_entry(
            'hacked_change_attempts_exceeded',
            track_id=self.track_id,
            action='hacked_change_attempts_exceeded',
            user_ip=TEST_IP,
            attempts='16',
        )

    def check_statbox_captcha_generation(self, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'captcha_generated',
                **kwargs
            ),
        ])

    def check_statbox_captcha_correctness(self, correct, reason='check', **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'captcha_checked',
                is_recognized=tskv_bool(correct),
                reason=reason,
                **kwargs
            ),
        ])


@with_settings_hosts(
    CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'lite',
        '': 'default',
    },
    CAPTCHA_COUNTRY_MATCHING={
        'ru': 'lite',
        '': 'default',
    },
    WAVE_CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'txt_v1',
        '': 'txt_v1_en',
    },
    WAVE_CAPTCHA_COUNTRY_MATCHING={
        'ru': 'txt_v1',
        '': 'txt_v1_en',
    },
    **mock_counters()
)
class TestCaptcha(BaseTestCaptcha):

    def test_empty_request(self):
        rv = self.env.client.get('/1/captcha/generate/', data={})
        eq_(rv.status_code, 400)

        rv = self.env.client.get('/1/captcha/check/', data={},
                                 headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 400)

    def test_captcha_errors(self):
        errors = (
            (400, captcha.CaptchaLocateError),
            (400, captcha.CaptchaTypeCheckError),
            (500, captcha.CaptchaAccessError),
            (503, captcha.CaptchaError),
            (503, captcha.CaptchaServerError),
            (503, captcha.CaptchaXmlParseError),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        for code, error in errors:
            self.env.captcha_mock.set_response_side_effect('check', error)
            self.env.captcha_mock.set_response_side_effect('generate', error)
            rv = self.env.client.get(self.generate_url)
            eq_(rv.status_code, code)

            rv = self.env.client.get(
                self.check_url,
                headers=mock_headers(user_ip=TEST_IP))
            eq_(rv.status_code, code)

    def test_correct_generate_request(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.uid = TEST_UID

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'lite', 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, None, 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(),
            'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        assert_is_none(track.is_captcha_checked)
        assert_is_none(track.is_captcha_recognized)

        self.check_statbox_captcha_generation(uid=TEST_UID)

    def test_correct_repeat_generate_request(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'lite', 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, None, 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(), 'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        eq_(track.is_captcha_checked, False)
        eq_(track.is_captcha_recognized, False)

        self.check_statbox_captcha_generation()

    def test_correct_generate_request_with_country(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url_with_country)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'lite', 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, None, 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(), 'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        eq_(track.is_captcha_checked, None)
        eq_(track.is_captcha_recognized, None)

        self.check_statbox_captcha_generation()

    @parameterized.expand([
        ('ru', 'wave', 'txt_v1'),
        ('us', 'wave', 'txt_v1_en'),
    ])
    def test_correct_generate_request_with_type_country(self, country, type, captcha_type):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url_with_type_country.format(country=country, type=type))
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, captcha_type, 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, None, 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(), 'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        eq_(track.is_captcha_checked, None)
        eq_(track.is_captcha_recognized, None)

        self.check_statbox_captcha_generation(image_type=captcha_type)

    @parameterized.expand([
        ('ru', 'wave', 'txt_v1'),
        ('en', 'wave', 'txt_v1_en'),
    ])
    def test_correct_generate_request_with_type_language(self, language, type, captcha_type):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url_with_type_language.format(language=language, type=type))
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, captcha_type, 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, None, 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(), 'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        eq_(track.is_captcha_checked, None)
        eq_(track.is_captcha_recognized, None)

        self.check_statbox_captcha_generation(image_type=captcha_type)

    def test_correct_generate_request_get_from_track_not_verified(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.captcha_generate_count.incr()
            track.captcha_generated_at = 123456789
            track.captcha_key = '1p'
            track.captcha_image_url = 'http://u.captcha.yandex.net/image?key=1p'
            track.captcha_voice_url = 'http://u.captcha.yandex.net/voice?key=1p'
            track.captcha_voice_intro_url = 'http://u.captcha.yandex.net/static/intro-ru.wav'

        self.env.captcha_mock.set_response_value('generate', None)
        rv = self.env.client.get(self.generate_url + '&voice=1&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'voice': {
                    'url': 'http://u.captcha.yandex.net/voice?key=1p',
                    'intro_url': 'http://u.captcha.yandex.net/static/intro-ru.wav',
                },
                'key': '1p',
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('captcha_used_cached'),
        ])

    def test_correct_generate_request_get_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            for _ in range(2):
                track.captcha_generate_count.incr()
            track.captcha_generated_at = 100
            track.captcha_key = '1p'
            track.captcha_image_url = 'http://u.captcha.yandex.net/image?key=1p'
            track.captcha_voice_url = 'http://u.captcha.yandex.net/voice?key=1p'
            track.captcha_voice_intro_url = 'http://u.captcha.yandex.net/static/intro-ru.wav'

        self.env.captcha_mock.set_response_value('generate', None)
        rv = self.env.client.get(self.generate_url + '&voice=1&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'voice': {
                    'url': 'http://u.captcha.yandex.net/voice?key=1p',
                    'intro_url': 'http://u.captcha.yandex.net/static/intro-ru.wav',
                },
                'key': '1p',
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('captcha_used_cached'),
        ])

    def test_correct_generate_request_no_use_cached_forced(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.captcha_generate_count.incr()
            track.captcha_key = 'test'
            track.captcha_image_url = 'test'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'key': '1p',
            },
        )

        self.check_statbox_captcha_generation()

    def test_correct_generate_request_no_use_cached_not_generated(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.captcha_key = 'test'
            track.captcha_image_url = 'test'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url + '&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'key': '1p',
            },
        )

        self.check_statbox_captcha_generation()

    def test_correct_generate_request_no_use_cached_already_checked(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            for _ in range(2):
                track.captcha_generate_count.incr()
            track.captcha_check_count.incr()
            track.captcha_generated_at = 99
            track.captcha_checked_at = 100
            track.is_captcha_checked = True
            track.captcha_key = 'test'
            track.captcha_image_url = 'test'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url + '&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'key': '1p',
            },
        )

        self.check_statbox_captcha_generation()

    def test_correct_generate_request_no_use_cached_captcha_invalidated(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            for _ in range(2):
                track.captcha_generate_count.incr()
            track.captcha_check_count.incr()
            track.captcha_generated_at = 99
            track.captcha_checked_at = 100
            track.is_captcha_checked = False
            track.captcha_key = 'test'
            track.captcha_image_url = None

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(self.generate_url + '&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'image_url': 'http://u.captcha.yandex.net/image?key=1p',
                'key': '1p',
            },
        )

        self.check_statbox_captcha_generation()

    def test_generate_cached__inconsistent_track_generate__ok(self):
        """
        Просим сгенерировать капчу с возможностью использовать закэшированную картинку
        В треке еще не сохранилось время генерации капчи, но уже увеличился счетчик
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.captcha_generate_count.incr()
            track.captcha_key = 'cached-key'
            track.captcha_image_url = 'cached-url'

        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)

        rv = self.env.client.get(self.generate_url + '&use_cached=1')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {'status': 'ok', 'image_url': 'http://u.captcha.yandex.net/image?key=1p', 'key': '1p'}
        )
        eq_(self.env.captcha_mock.request.call_count, 1)

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'lite', 'Captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 2, 'Captcha generator counter not incremented')
        eq_(track.captcha_generated_at, TimeNow(), 'Captcha generated timestamp not filled')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')
        assert_is_none(track.voice_captcha_type)
        assert_is_none(track.is_captcha_checked)
        assert_is_none(track.is_captcha_recognized)

        self.check_statbox_captcha_generation()

    def test_correct_generate_request_without_track(self):
        captcha_response = captcha_response_generate()
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get('/1/captcha/generate/?display_language=ru&consumer=dev')
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

    def test_correct_voice_request(self):
        captcha_response = captcha_voice_response_generate()

        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(
            path='/1/captcha/generate/',
            query_string={
                'consumer': 'dev',
                'track_id': self.track_id,
                'display_language': 'ru',
                'voice': '1',
            },
            headers=mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'voice': {
                    u'url': u'http://u.captcha.yandex.net/voice?key=1p',
                    u'intro_url': u'http://u.captcha.yandex.net/static/intro-ru.wav',
                },
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'lite', 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, 'ru', 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')

        self.check_statbox_captcha_generation(voice_type='ru')

    def test_correct_wave_voice_request(self):
        captcha_response = captcha_voice_response_generate()

        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(
            path='/1/captcha/generate/',
            query_string={
                'consumer': 'dev',
                'track_id': self.track_id,
                'display_language': 'ru',
                'voice': '1',
                'type': 'wave',
            },
            headers=mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'voice': {
                    u'url': u'http://u.captcha.yandex.net/voice?key=1p',
                    u'intro_url': u'http://u.captcha.yandex.net/static/intro-ru.wav',
                },
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.image_captcha_type, 'txt_v1', 'Captcha type not stored in track')
        eq_(track.voice_captcha_type, 'ru', 'Voice captcha type not stored in track')
        eq_(track.captcha_generate_count.get(), 1, 'Captcha generator counter not incremented')
        eq_(track.captcha_key, '1p', 'Captcha key not in track')

        self.check_statbox_captcha_generation(voice_type='ru', image_type='txt_v1')

    def test_correct_image_generate_request_with_en_language(self):
        captcha_response = captcha_response_generate()

        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(
            path='/1/captcha/generate/',
            query_string={
                'consumer': 'dev',
                'track_id': self.track_id,
                'display_language': 'en',
            },
            headers=mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        self.check_statbox_captcha_generation(image_type='default')

    def test_unsupported_voice_captcha_request(self):
        captcha_response = captcha_voice_response_generate()

        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(
            path='/1/captcha/generate/',
            query_string={
                'consumer': 'dev',
                'track_id': self.track_id,
                'country': 'DE',
                'voice': '1',
            },
            headers=mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'voice': {
                    u'warnings': [{
                        u'field': None,
                        u'message': u'Unsupported country=de for voice captcha',
                        u'code': u'unsupportedvoicecaptchacountry',
                    }],
                },
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        self.check_statbox_captcha_generation(image_type='default')

    def test_unsupported_voice_language_request(self):
        captcha_response = captcha_voice_response_generate()

        self.env.captcha_mock.set_response_value('generate', captcha_response)
        rv = self.env.client.get(
            path='/1/captcha/generate/',
            query_string={
                'consumer': 'dev',
                'track_id': self.track_id,
                'display_language': 'en',
                'voice': '1',
            },
            headers=mock_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'voice': {
                    u'warnings': [{
                        u'field': None,
                        u'message': u'Unsupported language=en for voice captcha',
                        u'code': u'unsupportedvoicecaptchalanguage',
                    }],
                },
                u'image_url': u'http://u.captcha.yandex.net/image?key=1p',
                u'key': '1p',
            },
        )

        self.check_statbox_captcha_generation(image_type='default')

    def test_correct_check_request(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.uid = TEST_UID

        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': True})

        track = self.track_manager.read(self.track_id)
        assert_true(track.is_captcha_checked)
        assert_true(track.is_captcha_recognized)
        eq_(track.captcha_checked_at, TimeNow())
        eq_(track.captcha_check_count.get(), 1)

        assert_builder_url_params_equal(
            self.env.captcha_mock,
            {
                'rep': 'a',
                'key': 'b',
                'client': 'passport-api',
                'request_id': mock.ANY,
            },
        )
        self.check_statbox_captcha_correctness(True, uid=TEST_UID)

    def test_correct_check_request_with_key_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.captcha_key = 'key'

        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(
            '/1/captcha/check/',
            query_string={
                'consumer': 'dev',
                'answer': 'a',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip=TEST_IP),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': True})

        track = self.track_manager.read(self.track_id)
        assert_true(track.is_captcha_checked)
        assert_true(track.is_captcha_recognized)
        eq_(track.captcha_checked_at, TimeNow())
        eq_(track.captcha_check_count.get(), 1)

        assert_builder_url_params_equal(
            self.env.captcha_mock,
            {
                'rep': 'a',
                'key': 'key',
                'client': 'passport-api',
                'request_id': mock.ANY,
            },
        )
        self.check_statbox_captcha_correctness(True, key='key')

    def test_check_request_without_key_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(
            '/1/captcha/check/',
            query_string={
                'consumer': 'dev',
                'answer': 'a',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip=TEST_IP),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': None,
                        u'message': u'Captcha key not provided',
                        u'code': u'emptycaptchakey',
                    },
                ],
            },
        )

    def test_failed_check_request(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        captcha_response = captcha_response_check(False)
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'correct': False})

        track = self.track_manager.read(self.track_id)
        assert_true(track.is_captcha_checked)
        assert_false(track.is_captcha_recognized)
        eq_(track.captcha_checked_at, TimeNow())
        eq_(track.captcha_check_count.get(), 1)
        self.check_statbox_captcha_correctness(False)

    def test_with_blacklisted_ip(self):
        captcha_response = captcha_response_check(True)
        self.env.captcha_mock.set_response_value('check', captcha_response)
        with mock.patch(
            'passport.backend.api.common.ip.is_ip_blacklisted',
            return_value=True,
        ):
            rv = self.env.client.get(self.check_url,
                                     headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'correct': False})

        track = self.track_manager.read(self.track_id)
        assert_true(track.is_captcha_checked)
        assert_false(track.is_captcha_recognized)
        eq_(track.captcha_checked_at, TimeNow())
        eq_(track.captcha_check_count.get(), 1)
        self.check_statbox_captcha_correctness(False, reason='bad_registration_as')

    def test_neither_ok_nor_failed_in_xml(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        self.env.captcha_mock.set_response_value(
            'check',
            u'''
            <?xml version='1.0'?>
            <image_check>^____^</image_check>
            '''.strip(),
        )

        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 503)

    def test_captcha_registration_karma(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'

        self.env.captcha_mock.set_response_value('check', captcha_response_check())
        bad_buckets = registration_karma.get_bad_buckets()
        good_buckets = registration_karma.get_good_buckets()

        def check_correct(correct):
            rv = self.env.client.get(self.check_url,
                                     headers=mock_headers(user_ip=TEST_IP))
            eq_(rv.status_code, 200)
            eq_(json.loads(rv.data), {'status': 'ok', 'correct': correct})

        for i in range(bad_buckets.limit - 1):
            registration_karma.incr_bad(TEST_IP)

        check_correct(True)

        registration_karma.incr_bad(TEST_IP)

        check_correct(False)

        # Пришёл хороший пользователь
        for i in range(good_buckets.limit - 1):
            registration_karma.incr_good(TEST_IP)

        check_correct(False)

        registration_karma.incr_good(TEST_IP)

        check_correct(True)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('captcha_checked'),

            self.env.statbox.entry('bad_reg_karma'),
            self.env.statbox.entry('captcha_checked', is_recognized='0', reason='bad_registration_karma'),

            self.env.statbox.entry('bad_reg_karma'),
            self.env.statbox.entry('captcha_checked', is_recognized='0', reason='bad_registration_karma'),

            self.env.statbox.entry('bad_reg_karma', onliner_status='amnisted_gray'),
            self.env.statbox.entry('captcha_checked'),
        ])

    def test_captcha_passed_for_test_yandex_login_ip_from_yandexnets(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'yandex-team'

        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip='37.9.101.188'))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': True})
        eq_(self.env.captcha_mock._mock.call_count, 0)
        self.check_statbox_captcha_correctness(True, reason='test_login')

    def test_captcha_passed_for_test_yandex_login_ip_from_grants(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'yandex-team'

        mocked_grants = mock_grants(grants={'captcha': ['*'], 'track': ['update']})
        mocked_grants.update(
            mock_grants(
                consumer='create_test_yandex_login_yandex-team',
                networks=['77.88.12.113'],
            )
        )

        self.env.grants.set_grants_return_value(mocked_grants)

        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip='77.88.12.113'))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': True})
        eq_(self.env.captcha_mock._mock.call_count, 0)
        self.check_statbox_captcha_correctness(True, reason='test_login')

    def test_captcha_not_passed_for_test_yandex_login_ip_from_world_with_uncorrect_captcha(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'yandex-team'

        captcha_response = captcha_response_check(False)
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip='213.87.129.27'))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': False})
        self.check_statbox_captcha_correctness(False)

    def test_correct_check_request_without_login(self):
        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip=TEST_IP))
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {u'status': u'ok', u'correct': True})
        self.check_statbox_captcha_correctness(True)


@with_settings_hosts(**mock_counters())
class TestHackedChangePassLimitsCaptcha(BaseTestCaptcha):

    def setUp(self):
        super(TestHackedChangePassLimitsCaptcha, self).setUp('authorize')

    def test_hacked_not_exceeding(self):
        """
        Проверяем, что смена пароля по причине взлома с не превышающим
        лимит счетчиком по IP не вызывает ошибок при проверке капчи
        и не увеличивает счетчик попыток на 1.
        """

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.change_password_reason = CHANGE_PASSWORD_REASON_HACKED

        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)

        rv = self.env.client.get(self.check_url,
                                 headers=mock_headers(user_ip=TEST_IP))

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'correct': True,
            }
        )
        counter = get_per_user_ip_buckets()
        eq_(counter.get(), 0)
        self.check_statbox_captcha_correctness(True)

    def test_hacked_exceeding(self):
        """
        Проверяем, что смена пароля по причине взлома с превышающим
        лимит счетчиком по IP вызывает выдачу ошибки при проверке капчи.
        """

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.change_password_reason = CHANGE_PASSWORD_REASON_HACKED
        counter = get_per_user_ip_buckets()
        for i in range(counter.limit + 1):
            counter.incr(TEST_IP)

        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        rv = self.env.client.get(
            self.check_url,
            headers=mock_headers(user_ip=TEST_IP),
        )
        counter = get_per_user_ip_buckets()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'correct': False,
            }
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('hacked_change_attempts_exceeded'),
            self.env.statbox.entry('captcha_checked', is_recognized='0', reason='hacked_change_attempts_exceeded'),
        ])

    def test_not_hacked_not_exceeding(self):
        """
        Проверяем, что смена пароля не по причине взлома с не превышающим
        лимит счетчиком по IP не вызывает выдачу ошибки при проверке капчи.
        """

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.change_password_reason = 'something-else-entirely'
        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)

        rv = self.env.client.get(
            self.check_url,
            headers=mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'correct': True,
            }
        )
        self.check_statbox_captcha_correctness(True)

    def test_not_hacked_exceeding(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'testlogin'
            track.change_password_reason = 'something-else-entirely'
        counter = get_per_user_ip_buckets()
        for i in range(counter.limit + 1):
            counter.incr(TEST_IP)
        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)

        rv = self.env.client.get(
            self.check_url,
            headers=mock_headers(user_ip=TEST_IP),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'ok',
                u'correct': True,
            }
        )
        self.check_statbox_captcha_correctness(True)
