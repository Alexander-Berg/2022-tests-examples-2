# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_all_tracks_response
from passport.backend.core.builders.blackbox.parsers import parse_blackbox_get_all_tracks_response
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
class TestBlackboxRequestGetAllTracks(BaseBlackboxRequestTestCase):

    def test_ok(self):
        self.set_blackbox_response_value(
            blackbox_get_all_tracks_response(),
        )
        response = self.blackbox.get_all_tracks(1)

        eq_(
            response,
            parse_blackbox_get_all_tracks_response(
                json.loads(
                    blackbox_get_all_tracks_response(),
                ),
            ),
        )

    def test_ok_empty(self):
        self.set_blackbox_response_value(
            blackbox_get_all_tracks_response(items=[]),
        )
        response = self.blackbox.get_all_tracks(1)

        eq_(
            response,
            [],
        )


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestGetAllTracksUrl(BaseBlackboxTestCase):

    def test_get_all_tracks_url(self):
        request_info = Blackbox().build_get_all_tracks_request(uid=42)
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

        check_all_url_params_match(
            request_info.url,
            {
                'uid': '42',
                'method': 'get_all_tracks',
                'format': 'json',
            },
        )
