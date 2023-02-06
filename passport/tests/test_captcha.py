# -*- coding: utf-8 -*-

from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.builders.base.faker.fake_builder import (
    assert_builder_requested,
    assert_builder_url_params_equal,
)
from passport.backend.core.builders.captcha import (
    Captcha,
    CaptchaAccessError,
    CaptchaError,
    CaptchaLocateError,
    CaptchaTypeCheckError,
    CaptchaXmlParseError,
)
from passport.backend.core.builders.captcha.captcha import (
    _get_scaled_image_type,
    _language_or_country_or_type,
    captcha_response,
    image_captcha,
    voice_captcha,
)
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
    captcha_voice_response_generate,
    FakeCaptcha,
)
from passport.backend.core.conf import settings
from passport.backend.core.logging_utils.faker.fake_tskv_logger import GraphiteLoggerFaker
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.core.useragent.faker.useragent import (
    FakedConnectionError,
    FakedHttpResponse,
    FakedTimeoutError,
    UserAgentFaker,
)
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)
from six import iteritems


@with_settings(
    CAPTCHA_URL=u'http://localhost/',
    CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'rus',
        'uk': 'nmixm',
        'us': 'nmixm',
        'tr': 'nmixm',
        '': 'nmixm',
    },
    CAPTCHA_COUNTRY_MATCHING={
        'kz': 'rus',
        'ua': 'rus',
        'by': 'rus',
        'ru': 'rus',
        '': 'nmixm',
    },
    CAPTCHA_VOICE_LANGUAGE_MATCHING={
        'ru': 'ru',
        'tr': 'tr',
        '': 'ru',
    },
    CAPTCHA_VOICE_COUNTRY_MATCHING={
        'ru': 'ru',
        'tr': 'tr',
        '': 'ru',
    },
    WAVE_CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'text_v1',
        '': 'text_v1_en',
    },
    WAVE_CAPTCHA_COUNTRY_MATCHING={
        'ru': 'text_v1',
        '': 'text_v1_en',
    },
    CAPTCHA_SCALE_MATCHING={
        'rus': {
            1.5: 'rus_scaled_1',
            2: 'rus_scaled_2',
            3: 'rus_scaled_3',
        },
    },
)
class TestCaptcha(TestCase):

    def setUp(self):
        self.faker = FakeCaptcha()
        self.faker.start()

        self.graphite_logger_faker = GraphiteLoggerFaker()
        self.graphite_logger_faker.start()

        self.captcha = Captcha()

    def tearDown(self):
        self.graphite_logger_faker.stop()
        self.faker.stop()
        del self.faker
        del self.graphite_logger_faker

    def set_xml_response(self, method, content_string):
        self.faker.set_response_value(
            method,
            u"""
            <?xml version='1.0'?>
            %s
            """.strip() % content_string,
        )

    def test_captcha_correct_recognize(self):
        self.faker.set_response_value('check', captcha_response_check())

        check = self.captcha.check(answer='applepie', key='')

        assert_builder_requested(self.faker, times=1)
        eq_(check, True)

    def test_captcha_correct_recognize_unicode_key(self):
        self.faker.set_response_value('check', captcha_response_check())

        check = self.captcha.check(answer=u'applepie', key=u'тест')

        assert_builder_requested(self.faker, times=1)
        eq_(check, True)

    def test_captcha_cyrillic_correct_recognize(self):
        self.faker.set_response_value('check', captcha_response_check())

        check = self.captcha.check(answer=u'фофудья', key='')

        assert_builder_requested(self.faker, times=1)
        eq_(check, True)

    def test_captcha_incorrect_recognize(self):
        self.faker.set_response_value(
            'check',
            captcha_response_check(successful=False),
        )

        check = self.captcha.check(answer='', key='')

        assert_builder_requested(self.faker, times=1)
        eq_(check, False)

    def test_captcha_invalid_xml(self):
        self.set_xml_response(
            'check',
            '<image_c/<he#nd>failed</image_check>',
        )

        with assert_raises(CaptchaXmlParseError):
            self.captcha.check(answer='', key='')
        assert_builder_requested(self.faker, times=1)

    def test_403_http_status_code(self):
        self.captcha.retries = 10
        self.faker.set_response_value(
            'check',
            mock.Mock(status_code=403),
        )
        with assert_raises(CaptchaAccessError):
            self.captcha.check('', '')
        assert_builder_requested(self.faker, times=1)

    def test_500_http_status_code(self):
        self.captcha.retries = 10
        self.faker.set_response_value(
            'check',
            mock.Mock(status_code=500),
        )
        with assert_raises(CaptchaError):
            self.captcha.check('', '')
        assert_builder_requested(self.faker, times=10)

    def test_502_http_status_code(self):
        self.captcha.retries = 10
        self.faker.set_response_value(
            'check',
            mock.Mock(status_code=502),
        )
        with assert_raises(CaptchaError):
            self.captcha.check('', '')
        assert_builder_requested(self.faker, times=10)

    def test_captcha_not_found(self):
        self.set_xml_response(
            'check',
            '<image_check error="not found">failed</image_check>',
        )

        with assert_raises(CaptchaLocateError):
            self.captcha.check(answer='', key='')
        assert_builder_requested(self.faker, times=1)

    def test_captcha_inconsistent_type(self):
        self.set_xml_response(
            'check',
            '<image_check error="inconsistent type">failed</image_check>',
        )

        with assert_raises(CaptchaTypeCheckError):
            self.captcha.check(answer='', key='')
        assert_builder_requested(self.faker, times=1)

    def test_captcha_blank_result(self):
        self.set_xml_response(
            'check',
            '<image_check> </image_check>',
        )

        with assert_raises(CaptchaError):
            self.captcha.check(answer='', key='')
        assert_builder_requested(self.faker, times=1)

    def test_captcha_undocumented_parameter(self):
        self.set_xml_response(
            'check',
            '<image_check error="destroy all humans">failed</image_check>',
        )

        with assert_raises(CaptchaError):
            self.captcha.check(answer='', key='')
        assert_builder_requested(self.faker, times=1)

    def test_captcha_invalid_characters_in_answer(self):
        self.faker.set_response_value(
            'check',
            '<image_check error="invalid characters in the user answer">failed</image_check>',
        )

        check = self.captcha.check(answer='', key='')

        assert_builder_requested(self.faker, times=1)
        eq_(check, False)

    def test_captcha_request(self):
        self.faker.set_response_value(
            'generate',
            captcha_response_generate(
                link='http://u.captcha.yandex.net/image?key=10pI',
                key='10pI',
            ),
        )

        generated = self.captcha.generate(image_type='rus', checks=3)

        assert_builder_requested(self.faker, times=1)
        eq_(
            generated,
            captcha_response(
                u'10pI',
                image_captcha(u'http://u.captcha.yandex.net/image?key=10pI', u'rus'),
                voice_captcha(None, None, None),
            ),
        )

    def test_captcha_request_with_https_and_request_id(self):
        self.faker.set_response_value(
            'generate',
            captcha_response_generate(
                link='https://u.captcha.yandex.net/image?key=10pI',
                key='10pI',
            ),
        )

        generated = self.captcha.generate(image_type='rus', checks=3, https=True, request_id='req-id')

        assert_builder_requested(self.faker, times=1)
        assert_builder_url_params_equal(
            self.faker,
            {'type': 'rus', 'checks': '3', 'https': 'on', 'client': 'passport-api', 'request_id': 'req-id'},
        )
        eq_(
            generated,
            captcha_response(
                u'10pI',
                image_captcha(u'https://u.captcha.yandex.net/image?key=10pI', u'rus'),
                voice_captcha(None, None, None),
            ),
        )

    def test_captcha_voice_request(self):
        self.faker.set_response_value(
            'generate',
            captcha_voice_response_generate(
                url='http://u.captcha.yandex.net/image?key=20d5',
                voice_url='http://u.captcha.yandex.net/voice?key=20d5',
                voice_intro_url='http://u.captcha.yandex.net/static/intro-ru.wav',
                key='20d5',
            ),
        )

        generated = self.captcha.generate(language='ru', checks=3, voice=True)
        assert_builder_requested(self.faker, times=1)
        eq_(
            generated,
            captcha_response(
                u'20d5',
                image_captcha(
                    u'http://u.captcha.yandex.net/image?key=20d5',
                    u'rus',
                ),
                voice_captcha(
                    u'http://u.captcha.yandex.net/voice?key=20d5',
                    u'http://u.captcha.yandex.net/static/intro-ru.wav',
                    u'ru',
                ),
            ),
        )

    def test_captcha_wave_voice_request(self):
        self.faker.set_response_value(
            'generate',
            captcha_voice_response_generate(
                url='http://u.captcha.yandex.net/image?key=20d5',
                voice_url='http://u.captcha.yandex.net/voice?key=20d5',
                voice_intro_url='http://u.captcha.yandex.net/static/intro-ru.wav',
                key='20d5',
            ),
        )

        generated = self.captcha.generate(image_type='wave', language='ru', checks=3, voice=True)
        assert_builder_requested(self.faker, times=1)
        eq_(
            generated,
            captcha_response(
                u'20d5',
                image_captcha(
                    u'http://u.captcha.yandex.net/image?key=20d5',
                    u'text_v1',
                ),
                voice_captcha(
                    u'http://u.captcha.yandex.net/voice?key=20d5',
                    u'http://u.captcha.yandex.net/static/intro-ru.wav',
                    u'ru',
                ),
            ),
        )

    def test_captcha_request_error(self):
        self.captcha.retries = 10
        self.faker.set_response_side_effect('check', RequestError())
        with assert_raises(CaptchaError):
            self.captcha.check('', '')
        assert_builder_requested(self.faker, times=10)

    @raises(ValueError)
    def test_captcha_generate_redundant_parameters(self):
        self.captcha.generate(image_type='rus', language='ru', country='RU', checks=3)

    @raises(ValueError)
    def test_captcha_voice_generate_redundant_parameters(self):
        self.captcha.generate(voice_type='ru', language='ru', country='RU', checks=3)

    @raises(ValueError)
    def test_captcha_generate_abundant_parameters(self):
        self.captcha.generate(checks=3)

    @raises(ValueError)
    def test_captcha_check_abundant_parameters(self):
        self.captcha.check(answer='', key='')

    def test_check_type_detection_by_language(self):
        for language, type_ in iteritems(settings.CAPTCHA_LANGUAGE_MATCHING):
            eq_(
                _language_or_country_or_type(
                    'test_check_type_detection',
                    language=language,
                    data_type_by_language=settings.CAPTCHA_LANGUAGE_MATCHING,
                    data_type_by_country=settings.CAPTCHA_COUNTRY_MATCHING,
                    wave_type_by_language=settings.WAVE_CAPTCHA_LANGUAGE_MATCHING,
                    wave_type_by_country=settings.WAVE_CAPTCHA_COUNTRY_MATCHING,
                ),
                type_,
            )

    def test_check_type_detection_by_country(self):
        for country, type_ in iteritems(settings.CAPTCHA_COUNTRY_MATCHING):
            eq_(
                _language_or_country_or_type(
                    'test_check_type_detection',
                    country=country,
                    data_type_by_language=settings.CAPTCHA_LANGUAGE_MATCHING,
                    data_type_by_country=settings.CAPTCHA_COUNTRY_MATCHING,
                    wave_type_by_language=settings.WAVE_CAPTCHA_LANGUAGE_MATCHING,
                    wave_type_by_country=settings.WAVE_CAPTCHA_COUNTRY_MATCHING,
                ),
                type_,
            )

    def test_check_type_detection_by_country_unknown_country(self):
        eq_(
            _language_or_country_or_type(
                'test_check_type_detection',
                country='USSR',
                data_type_by_language=settings.CAPTCHA_LANGUAGE_MATCHING,
                data_type_by_country=settings.CAPTCHA_COUNTRY_MATCHING,
                wave_type_by_language=settings.WAVE_CAPTCHA_LANGUAGE_MATCHING,
                wave_type_by_country=settings.WAVE_CAPTCHA_COUNTRY_MATCHING,
            ),
            settings.CAPTCHA_COUNTRY_MATCHING[''],
        )

    def test_check_image_type_with_scale(self):
        for scale in [1.5, 2, 3]:
            eq_(
                _get_scaled_image_type(
                    'rus',
                    scale,
                ),
                'rus_scaled_%d' % scale,
            )

    def test_check_image_type_with_unknown_scale__ignore_scale(self):
        UNKNOWN_SCALE = 100500
        eq_(
            _get_scaled_image_type(
                'rus',
                UNKNOWN_SCALE,
            ),
            'rus',
        )

    def test_check_voice_type_detection_by_language(self):
        for language, type_ in iteritems(settings.CAPTCHA_VOICE_LANGUAGE_MATCHING):
            eq_(
                _language_or_country_or_type(
                    'test_check_type_detection',
                    language=language,
                    data_type_by_language=settings.CAPTCHA_VOICE_LANGUAGE_MATCHING,
                    data_type_by_country=settings.CAPTCHA_VOICE_COUNTRY_MATCHING,
                    wave_type_by_language=settings.WAVE_CAPTCHA_LANGUAGE_MATCHING,
                    wave_type_by_country=settings.WAVE_CAPTCHA_COUNTRY_MATCHING,
                ),
                type_,
            )

    def test_check_voice_type_detection_by_country(self):
        for country, type_ in iteritems(settings.CAPTCHA_VOICE_COUNTRY_MATCHING):
            eq_(
                _language_or_country_or_type(
                    'test_check_type_detection',
                    country=country,
                    data_type_by_language=settings.CAPTCHA_VOICE_LANGUAGE_MATCHING,
                    data_type_by_country=settings.CAPTCHA_VOICE_COUNTRY_MATCHING,
                    wave_type_by_language=settings.WAVE_CAPTCHA_LANGUAGE_MATCHING,
                    wave_type_by_country=settings.WAVE_CAPTCHA_COUNTRY_MATCHING,
                ),
                type_,
            )


@with_settings(
    CAPTCHA_URL=u'http://localhost/',
)
class CaptchaUsesGraphiteLoggerTestCase(TestCase):

    def setUp(self):
        self.graphite_logger_mock = mock.Mock()
        self.graphite_logger_mock.make_context = mock.Mock(return_value=mock.MagicMock())
        self.GraphiteLoggerMock = mock.Mock(return_value=self.graphite_logger_mock)

    def tearDown(self):
        del self.graphite_logger_mock
        del self.GraphiteLoggerMock

    def test_captcha_initialize_graphite_logger(self):
        with mock.patch(
            'passport.backend.core.builders.captcha.captcha.GraphiteLogger',
            self.GraphiteLoggerMock
        ):
            captcha = Captcha()

        self.GraphiteLoggerMock.assert_called_with(service='captcha')
        eq_(captcha.graphite_logger, self.graphite_logger_mock)


@with_settings(
    CAPTCHA_URL=u'http://localhost/',
    CAPTCHA_RETRIES=2,
    CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'rus',
        'uk': 'nmixm',
        'us': 'nmixm',
        'tr': 'nmixm',
    },
    CAPTCHA_COUNTRY_MATCHING={
        'KZ': 'rus',
        'UA': 'rus',
        'BY': 'rus',
        'RU': 'rus',
        '': 'nmixm',
    },
    WAVE_CAPTCHA_LANGUAGE_MATCHING={
        'ru': 'text_v1',
        '': 'text_v1_en',
    },
    WAVE_CAPTCHA_COUNTRY_MATCHING={
        'ru': 'text_v1',
        '': 'text_v1_en',
    },
    CAPTCHA_VOICE_LANGUAGE_MATCHING={
        'ru': 'ru',
        'tr': 'tr',
    },
    CAPTCHA_VOICE_COUNTRY_MATCHING={
        'RU': 'ru',
        'TR': 'tr',
        '': 'ru',
    },
    CAPTCHA_SCALE_MATCHING={
        'rus': {},
    }
)
class CaptchaIntegrationWithGraphiteLoggerTestCase(TestCase):
    about_zero_seconds = TimeSpan(0)

    def setUp(self):
        self._patches = []

        self.graphite_logger_faker = GraphiteLoggerFaker()
        self.graphite_logger_faker.start()
        self._patches.append(self.graphite_logger_faker)

        self.user_agent_faker = UserAgentFaker()
        self.user_agent_faker.start()
        self._patches.append(self.user_agent_faker)

        self.captcha = Captcha(useragent=UserAgent())

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()
        del self._patches
        del self.graphite_logger_faker
        del self.user_agent_faker
        del self.captcha

    def test_check_reports_success(self):
        self.user_agent_faker.set_responses([
            FakedHttpResponse(
                200,
                content="<?xml version='1.0'?><image_check>ok</image_check>",
            ),
        ])
        self.captcha.check(answer='applepie', key='')

        self.graphite_logger_faker.assert_has_written(
            [
                {
                    'retries_left': '1',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'tskv_format': 'passport-log',
                    'response': 'success',
                    'http_code': '200',
                    'duration': self.about_zero_seconds,
                    'network_error': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
            ],
        )

    def test_check_reports_fail_and_timeout(self):
        self.user_agent_faker.set_responses([
            FakedConnectionError(),
            FakedTimeoutError(),
        ])
        with assert_raises(CaptchaError):
            self.captcha.check(answer='applepie', key='')

        self.graphite_logger_faker.assert_has_written(
            [
                {
                    'retries_left': '1',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'response': 'failed',
                    'duration': self.about_zero_seconds,
                    'tskv_format': 'passport-log',
                    'network_error': '1',
                    'http_code': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
                {
                    'retries_left': '0',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'response': 'timeout',
                    'duration': self.about_zero_seconds,
                    'tskv_format': 'passport-log',
                    'network_error': '1',
                    'http_code': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
            ],
        )

    def test_check_reports_success_and_retry(self):
        self.user_agent_faker.set_responses([
            FakedTimeoutError(),
            FakedHttpResponse(
                200,
                content="<?xml version='1.0'?><image_check>ok</image_check>",
            ),
        ])
        self.captcha.check(answer='applepie', key='')

        self.graphite_logger_faker.assert_has_written(
            [
                {
                    'retries_left': '1',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'tskv_format': 'passport-log',
                    'response': 'timeout',
                    'http_code': '0',
                    'duration': self.about_zero_seconds,
                    'network_error': '1',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
                {
                    'retries_left': '0',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'tskv_format': 'passport-log',
                    'response': 'success',
                    'http_code': '200',
                    'duration': self.about_zero_seconds,
                    'network_error': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
            ],
        )

    def test_generate_reports_fail_and_timeout(self):
        self.user_agent_faker.set_responses([
            FakedConnectionError(),
            FakedTimeoutError(),
        ])
        with assert_raises(CaptchaError):
            self.captcha.generate(image_type='rus', checks=3)

        self.graphite_logger_faker.assert_has_written(
            [
                {
                    'retries_left': '1',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'response': 'failed',
                    'duration': self.about_zero_seconds,
                    'tskv_format': 'passport-log',
                    'network_error': '1',
                    'http_code': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
                {
                    'retries_left': '0',
                    'unixtime': self.graphite_logger_faker.get_unixtime_mock(),
                    'service': 'captcha',
                    'response': 'timeout',
                    'duration': self.about_zero_seconds,
                    'tskv_format': 'passport-log',
                    'network_error': '1',
                    'http_code': '0',
                    'srv_hostname': 'localhost',
                    'srv_ipaddress': '127.0.0.1',
                    'timestamp': self.graphite_logger_faker.get_timestamp_mock(),
                },
            ],
        )
