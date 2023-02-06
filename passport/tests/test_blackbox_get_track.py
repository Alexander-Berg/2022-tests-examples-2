# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_track_response
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestGetTrack(BaseBlackboxRequestTestCase):

    def test_track_found(self):
        self.set_blackbox_response_value(
            blackbox_get_track_response(1, 'track_id'),
        )
        response = self.blackbox.get_track(1, 'track_id')

        eq_(
            response,
            json.loads(
                blackbox_get_track_response(1, 'track_id'),
            ),
        )

    def test_track_not_found(self):
        self.set_blackbox_response_value(
            blackbox_get_track_response(1, 'track_id', content=None),
        )
        response = self.blackbox.get_track(1, 'track_id')

        eq_(
            response,
            json.loads(
                blackbox_get_track_response(1, 'track_id', content=None),
            ),
        )


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestGetTrackUrl(BaseBlackboxTestCase):

    def test_get_track_url(self):
        request_info = Blackbox().build_get_track_request(uid=42, track_id='track_id')
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

        check_all_url_params_match(
            request_info.url,
            {
                'uid': '42',
                'track_id': 'track_id',
                'method': 'get_track',
                'format': 'json',
            },
        )
