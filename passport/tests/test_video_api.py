# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.video import VideoSearchApi
from passport.backend.core.builders.video.exceptions import (
    RequestTooLongError,
    VideoApiPermanentError,
    VideoApiXmlParseError,
)
from passport.backend.core.builders.video.faker import (
    FakeVideoSearchApi,
    video_empty_response,
    video_info_error_response,
    video_info_successful_response,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    VIDEO_API_URL='http://localhost/',
    VIDEO_API_TIMEOUT=0.5,
    VIDEO_API_RETRIES=2,
)
class TestVideoApiCommon(unittest.TestCase):
    def setUp(self):
        self.video_api = VideoSearchApi()
        self.video_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.video_api.useragent.request.return_value = self.response
        self.video_api.useragent.request_error_class = self.video_api.temporary_error_class
        self.response.content = video_info_successful_response('url1', [])
        self.response.status_code = 200

    def tearDown(self):
        del self.video_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'not xml'
        with assert_raises(VideoApiXmlParseError):
            self.video_api.video_info(urls=['test'])

    def test_server_error(self):
        self.response.status_code = 503
        with assert_raises(VideoApiPermanentError):
            self.video_api.video_info(urls='test')

    def test_bad_status_code(self):
        self.response.status_code = 418
        with assert_raises(VideoApiPermanentError):
            self.video_api.video_info(urls='test')

    def test_error_code(self):
        self.response.content = video_info_error_response()
        with assert_raises(VideoApiPermanentError):
            self.video_api.video_info(urls='test')

    def test_request_too_long(self):
        self.response.content = video_info_error_response(error_code='10001', text=u'Не больше 400 символов')
        with assert_raises(RequestTooLongError):
            self.video_api.video_info(urls='test')

    def test_not_found_ok(self):
        self.response.content = video_info_error_response(error_code='15', text=u'Не встречается')
        ok_(not self.video_api.video_info(urls='test'))


@with_settings(
    VIDEO_API_URL='http://localhost/',
    VIDEO_API_TIMEOUT=0.5,
    VIDEO_API_RETRIES=2,
)
class TestVideoApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_video_api = FakeVideoSearchApi()
        self.fake_video_api.start()

        self.video_api = VideoSearchApi()

    def tearDown(self):
        self.fake_video_api.stop()
        del self.fake_video_api

    def test_video_info_ok(self):
        url = u'http://www.youtube.com/watch?v=WSebDJ9lAC0'
        results = [
            {
                'url': url,
                'title': u'Рик и Морти - философия мультсериала',
                'description': u'рик и морти, рик и морти...',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'http://video-tub-ru.yandex.net/i?id=24de430e48e785c47ce5711c850e24fc-00-96',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        self.fake_video_api.set_response_value(
            'video_info',
            video_info_successful_response(url, results),
        )
        response = self.video_api.video_info(urls=url)
        expected_response = results[:]
        expected_response[0]['hd'] = True
        eq_(response, expected_response)

        eq_(len(self.fake_video_api.requests), 1)
        self.fake_video_api.requests[0].assert_url_starts_with(
            'http://localhost/search/xml',
        )
        self.fake_video_api.requests[0].assert_query_equals({
            'type': 'video',
            'text': 'url:\"{}\"'.format(url),
            'family': 'none',
        })

    def test_empty_response(self):
        self.fake_video_api.set_response_value(
            'video_info',
            video_empty_response(),
        )
        response = self.video_api.video_info(urls='url')
        ok_(not response)

        eq_(len(self.fake_video_api.requests), 1)
        self.fake_video_api.requests[0].assert_url_starts_with(
            'http://localhost/search/xml',
        )
        self.fake_video_api.requests[0].assert_query_equals({
            'type': 'video',
            'text': 'url:"url"',
            'family': 'none',
        })

    def test_multiple_urls_ok(self):
        urls = [
            u'http://www.youtube.com/watch?v=WSebDJ9lAC0',
            u'https://www.youtube.com/watch?v=Bf_7gWpMxSg',
            u'fake_url',
        ]
        results = [
            {
                'url': u'http://www.youtube.com/watch?v=WSebDJ9lAC0',
                'title': u'Рик и Морти - философия мультсериала',
                'description': u'рик и морти, рик и морти...',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'http://video-tub-ru.yandex.net/i?id=24de430e48e785c47ce5711c850e24fc-00-96',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
            {
                'url': u'https://www.youtube.com/watch?v=Bf_7gWpMxSg',
                'title': u'[BadComedian] - СПАСТИ ПУШКИНА',
                'description': u'',
                'duration': u'weird',
                'hd': u'0',
                'id': u'2',
                'thumbnail': u'http://video-tub-ru.yandex.net/i?id=a31411b4860cd35f988354b0fd7adbd9-00-96',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        self.fake_video_api.set_response_value(
            'video_info',
            video_info_successful_response(urls, results),
        )
        response = self.video_api.video_info(urls=urls)
        expected_response = results[:]
        expected_response[1].pop('description')
        expected_response[1].pop('duration')
        expected_response[0]['hd'] = True
        expected_response[1]['hd'] = False
        eq_(response, expected_response)

        eq_(len(self.fake_video_api.requests), 1)
        self.fake_video_api.requests[0].assert_url_starts_with(
            'http://localhost/search/xml',
        )
        self.fake_video_api.requests[0].assert_query_equals({
            'type': 'video',
            'family': 'none',
            'text': 'url:"http://www.youtube.com/watch?v=WSebDJ9lAC0"|'
                    'url:"https://www.youtube.com/watch?v=Bf_7gWpMxSg"|url:"fake_url"',
        })

    def test_empty_group(self):
        urls = [
            u'http://www.youtube.com/watch?v=WSebDJ9lAC0',
            u'https://www.youtube.com/watch?v=123',
        ]
        results = [
            {
                'url': u'http://www.youtube.com/watch?v=WSebDJ9lAC0',
                'title': u'Рик и Морти - философия мультсериала',
                'description': u'рик и морти, рик и морти...',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'http://video-tub-ru.yandex.net/i?id=24de430e48e785c47ce5711c850e24fc-00-96',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
            {
                'url': u'https://www.youtube.com/watch?v=123',
                'id': u'2222',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
            {
                'url': u'https://',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        self.fake_video_api.set_response_value(
            'video_info',
            video_info_successful_response(urls, results),
        )
        response = self.video_api.video_info(urls=urls)
        expected_response = results[:]
        expected_response[0]['hd'] = True
        expected_response[1]['hd'] = False
        expected_response.pop(2)
        eq_(response, expected_response)

        eq_(len(self.fake_video_api.requests), 1)
        self.fake_video_api.requests[0].assert_url_starts_with(
            'http://localhost/search/xml',
        )
        self.fake_video_api.requests[0].assert_query_equals({
            'type': 'video',
            'family': 'none',
            'text': 'url:"http://www.youtube.com/watch?v=WSebDJ9lAC0"|'
                    'url:"https://www.youtube.com/watch?v=123"',
        })
