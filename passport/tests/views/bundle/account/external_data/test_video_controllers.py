# -*- coding: utf-8 -*-
from copy import deepcopy

from nose.tools import istest
from passport.backend.core.builders.datasync_api import DatasyncApiTemporaryError
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import video_favorites_successful_response
from passport.backend.core.builders.video import (
    RequestTooLongError,
    VideoApiTemporaryError,
)
from passport.backend.core.builders.video.faker import video_info_successful_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_TOKEN_HEADERS,
    TEST_TVM_TICKET_OTHER,
    TEST_UID,
)


TEST_DATASYNC_API_URL = 'https://disk.net'
TEST_VIDEO_API_URL = 'https://search.yandex.net'

TEST_VIDEO_INFO = {
    'url': u'http://www.youtube.com/watch?v=WSebDJ9lAC0',
    'title': u'Рик и Морти - философия мультсериала',
    'description': u'рик и морти, рик и морти...',
    'duration': 1155,
    'hd': '1',
    'id': '100500',
    'thumbnail': u'http://video-tub-ru.yandex.net/i?id=24de430e48e785c47ce5711c850e24fc-00-96',
    'thumbnail_width': 480,
    'thumbnail_height': 360,
}

TEST_EXPECTED_RESPONSE = dict(
    TEST_VIDEO_INFO,
    hd=True,
    thumbnail=u'//video-tub-ru.yandex.net/i?id=24de430e48e785c47ce5711c850e24fc-00-96',
)


@istest
@with_settings_hosts(
    DATASYNC_API_URL=TEST_DATASYNC_API_URL,
    VIDEO_API_URL=TEST_VIDEO_API_URL,
)
class VideoFavouritesTestCase(BaseExternalDataTestCase):
    default_url = '/1/bundle/account/external_data/video/favourites/'
    http_query_args = dict(
        consumer='dev',
    )
    oauth_scope = 'oauth:grant_xtoken'

    def setUp(self):
        super(VideoFavouritesTestCase, self).setUp()
        self.env.personality_api.set_response_value(
            'video_favorites',
            video_favorites_successful_response(),
        )
        self.env.video_search_api.set_response_value(
            'video_info',
            video_info_successful_response(
                query='url1|url2',
                data=[TEST_VIDEO_INFO],
            ),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            videos=[TEST_EXPECTED_RESPONSE],
        )
        self.env.personality_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/personality/profile/videosearch/likes?limit=10&offset=0&query.order.asc=False' % (
                TEST_DATASYNC_API_URL,
            ),
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )
        self.env.video_search_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/search/xml?type=video&family=none&text=url:"url"|url:"http://www.youtube.com/watch?v=WSebDJ9lAC0"' % (
                TEST_VIDEO_API_URL,
            ),
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            videos=[TEST_EXPECTED_RESPONSE],
        )
        self.env.personality_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/personality/profile/videosearch/likes?limit=20&offset=40&query.order.asc=False' % (
                TEST_DATASYNC_API_URL,
            ),
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )
        self.env.video_search_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/search/xml?type=video&family=none&text=url:"url"|url:"http://www.youtube.com/watch?v=WSebDJ9lAC0"' % (
                TEST_VIDEO_API_URL,
            ),
        )

    def test_datasync_api_unavailable(self):
        self.env.personality_api.set_response_side_effect(
            'video_favorites',
            DatasyncApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.datasync_api_failed'])

    def test_video_api_unavailable(self):
        self.env.video_search_api.set_response_side_effect(
            'video_info',
            VideoApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.video_api_failed'])

    def test_page_too_large(self):
        self.env.video_search_api.set_response_side_effect(
            'video_info',
            RequestTooLongError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['page_size.too_large'])

    def test_no_videos(self):
        self.env.personality_api.set_response_value(
            'video_favorites',
            video_favorites_successful_response(items=[]),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            videos=[],
        )

    def test_videos_not_found(self):
        self.env.video_search_api.set_response_value(
            'video_info',
            video_info_successful_response(
                query='url1|url2',
                data=[],
            ),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            videos=[],
        )

    def test_no_thumbnail_ok(self):
        cut_data = deepcopy(TEST_VIDEO_INFO)
        cut_data.pop('thumbnail')
        self.env.video_search_api.set_response_value(
            'video_info',
            video_info_successful_response(
                query='url1|url2',
                data=[cut_data],
            ),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        expected = deepcopy(TEST_EXPECTED_RESPONSE)
        expected.pop('thumbnail')
        self.assert_ok_response(
            rv,
            videos=[expected],
        )
        self.env.personality_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/personality/profile/videosearch/likes?limit=10&offset=0&query.order.asc=False' % (
                TEST_DATASYNC_API_URL,
            ),
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )
        self.env.video_search_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/search/xml?type=video&family=none&text=url:"url"|url:"http://www.youtube.com/watch?v=WSebDJ9lAC0"' % (
                TEST_VIDEO_API_URL,
            ),
        )
