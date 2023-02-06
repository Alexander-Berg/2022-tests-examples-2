# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.video import VideoSearchApi
from passport.backend.core.builders.video.exceptions import VideoApiPermanentError
from passport.backend.core.builders.video.faker import (
    FakeVideoSearchApi,
    video_empty_response,
    video_info_error_response,
    video_info_successful_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 123


EXPECTED_XML = u"""<yandexsearch>
  <request>
    <query>url:"url"</query>
  </request>
  <response>
    <results>
      <grouping>
        <group>
          <doc>
            <url>url</url>
            <title>Test Title</title>
            <passages>
              <passage>desc</passage>
            </passages>
            <properties>
              <MediaDuration>1155</MediaDuration>
              <vhdbin>1</vhdbin>
              <videoid>1</videoid>
            </properties>
            <image-properties>
              <thumbnail-link>pic1</thumbnail-link>
              <thumbnail-width-original>480</thumbnail-width-original>
              <thumbnail-height-original>360</thumbnail-height-original>
            </image-properties>
          </doc>
        </group>
      </grouping>
    </results>
  </response>
</yandexsearch>
"""


@with_settings(
    VIDEO_API_RETRIES=2,
    VIDEO_API_TIMEOUT=1,
    VIDEO_API_URL='http://localhost/',
)
class FakeVideoApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeVideoSearchApi()
        self.faker.start()
        self.video_api = VideoSearchApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.video_api

    def test_xml_builder(self):
        result = [
            {
                'url': u'url',
                'title': u'Test Title',
                'description': u'desc',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'pic1',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        eq_(
            video_info_successful_response('url', result),
            EXPECTED_XML.encode('utf8'),
        )

    def test_video_info_one_response(self):
        results = [
            {
                'url': u'url',
                'title': u'Test Title',
                'description': u'desc',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'pic1',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        self.faker.set_response_value(
            'video_info',
            video_info_successful_response('url', results),
        )
        expected_response = results[:]
        expected_response[0]['hd'] = True

        eq_(
            self.video_api.video_info('url'),
            expected_response,
        )

    def test_video_info_multiple_response(self):
        urls = ['url-1', 'url-2']
        results = [
            {
                'url': u'url-1',
                'title': u'Title 1',
                'description': u'',
                'duration': 1155,
                'hd': '1',
                'id': '1',
                'thumbnail': u'pic-1',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
            {
                'url': u'url-2',
                'title': u'Test title',
                'description': u'Desc test',
                'duration': 180,
                'hd': '',
                'id': '2',
                'thumbnail': u'pic-2',
                'thumbnail_width': 480,
                'thumbnail_height': 360,
            },
        ]
        self.faker.set_response_value(
            'video_info',
            video_info_successful_response(urls, results),
        )
        expected_response = results[:]
        expected_response[0].pop('description')
        expected_response[0]['hd'] = True
        expected_response[1]['hd'] = False

        eq_(
            self.video_api.video_info(urls),
            results,
        )

    def test_video_info_no_groups_response(self):
        self.faker.set_response_value(
            'video_info',
            video_info_successful_response('test-url', []),
        )

        eq_(self.video_api.video_info('test-url'), [])

    def test_video_info_empty_response(self):
        self.faker.set_response_value(
            'video_info',
            video_empty_response(),
        )

        eq_(self.video_api.video_info('url'), [])

    def test_error_response(self):
        self.faker.set_response_value(
            'video_info',
            video_info_error_response(),
        )
        with assert_raises(VideoApiPermanentError):
            self.video_api.video_info('test')

    def test_not_found(self):
        self.faker.set_response_value(
            'video_info',
            video_info_error_response(error_code='15'),
        )
        eq_(self.video_api.video_info('test-url'), [])
