# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.common.exception import (
    ProviderCommunicationProxylibError,
    ProviderRateLimitExceededProxylibError,
)
from passport.backend.social.proxylib import get_proxy

from . import TestProxy


class TestProxyTwitter(TestProxy):
    provider_code = 'tw'

    error_profile_response = '{"errors":[{"message":"Bad Authentication data","code":215}]}'

    def test_profile(self):

        decoded_data = """
            {
              "id": 1464326220,
              "id_str": "1464326220",
              "name": "%(name)s",
              "screen_name": "PetrTestov",
              "location": "",
              "description": "",
              "url": null,
              "entities": {
                "description": {
                  "urls": []
                }
              },
              "protected": false,
              "followers_count": 1,
              "friends_count": 22,
              "listed_count": 0,
              "created_at": "Tue May 28 10:32:35 +0000 2013",
              "favourites_count": 0,
              "utc_offset": null,
              "time_zone": null,
              "geo_enabled": false,
              "verified": false,
              "statuses_count": 229,
              "lang": "en",
              "status": {
                "created_at": "Sat Oct 19 16:42:30 +0000 2013",
                "id": 391605287947231200,
                "id_str": "391605287947231233",
                "text": "text",
                "source": "web",
                "truncated": false,
                "in_reply_to_status_id": null,
                "in_reply_to_status_id_str": null,
                "in_reply_to_user_id": null,
                "in_reply_to_user_id_str": null,
                "in_reply_to_screen_name": null,
                "geo": null,
                "coordinates": null,
                "place": null,
                "contributors": null,
                "retweet_count": 0,
                "favorite_count": 0,
                "entities": {
                  "hashtags": [],
                  "symbols": [],
                  "urls": [
                    {
                      "url": "http://t.co/Xi7PGw0pHF",
                      "expanded_url": "http://ceumjiao.tumblr.com/post/",
                      "display_url": "ceumjiao.tumblr.com/post/",
                      "indices": [
                        57,
                        79
                      ]
                    }
                  ],
                  "user_mentions": []
                },
                "favorited": false,
                "retweeted": false,
                "possibly_sensitive": false,
                "lang": "ru"
              },
              "contributors_enabled": false,
              "is_translator": false,
              "profile_background_color": "C0DEED",
              "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
              "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
              "profile_background_tile": false,
              "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
              "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
              "profile_link_color": "0084B4",
              "profile_sidebar_border_color": "C0DEED",
              "profile_sidebar_fill_color": "DDEEF6",
              "profile_text_color": "333333",
              "profile_use_background_image": true,
              "default_profile": true,
              "default_profile_image": true,
              "following": false,
              "follow_request_sent": false,
              "notifications": false
            }
        """

        expected_dict = {u'username': u'PetrTestov', u'firstname': u'Petr', u'lastname': u'Testov',
                         u'userid': '1464326220', u'avatar': {}, 'followers_count': 1, 'friends_count': 22,
                         'messages_count': 229}
        self._process_single_test(
            'get_profile',
            decoded_data % {'name': 'Petr Testov'},
            expected_dict=expected_dict,
        )

        data = self._process_single_test(
            'get_profile',
            decoded_data % {'name': 'Petr'},
        )
        ok_('lastname' not in data)
        eq_(data['firstname'], 'Petr')

    def test_profile_error(self):
        self._tst_profile_error()

    def test_get_friends(self):
        decoded_data = """
            {
              "users": [
                {
                  "id": 74286565,
                  "id_str": "74286565",
                  "name": "Microsoft",
                  "screen_name": "Microsoft",
                  "location": "Redmond, WA",
                  "url": "http://www.facebook.com/Microsoft",
                  "description": "The official.",
                  "protected": false,
                  "followers_count": 3933376,
                  "friends_count": 1054,
                  "listed_count": 11231,
                  "created_at": "Mon Sep 14 22:35:42 +0000 2009",
                  "favourites_count": 104,
                  "utc_offset": -28800,
                  "time_zone": "Pacific Time (US & Canada)",
                  "geo_enabled": false,
                  "verified": true,
                  "statuses_count": 7140,
                  "lang": "en",
                  "contributors_enabled": false,
                  "is_translator": false,
                  "profile_background_color": "00AEEF",
                  "profile_background_image_url": "http://a0.twimg.com/profile_background_images/431832285/Twitter_BG_1040x2000.png",
                  "profile_background_image_url_https": "https://si0.twimg.com/profile_background_images/431832285/Twitter_BG_1040x2000.png",
                  "profile_background_tile": false,
                  "profile_image_url": "http://pbs.twimg.com/profile_images/2535822544/secztwqh31xo8xydi4kq_normal.png",
                  "profile_image_url_https": "https://pbs.twimg.com/profile_images/2535822544/secztwqh31xo8xydi4kq_normal.png",
                  "profile_banner_url": "https://pbs.twimg.com/profile_banners/74286565/1378498247",
                  "profile_link_color": "1570A6",
                  "profile_sidebar_border_color": "8FC642",
                  "profile_sidebar_fill_color": "FFFFFF",
                  "profile_text_color": "333333",
                  "profile_use_background_image": true,
                  "default_profile": false,
                  "default_profile_image": false,
                  "following": true,
                  "follow_request_sent": false,
                  "notifications": false
                }
              ],
              "next_cursor": 0,
              "next_cursor_str": "0",
              "previous_cursor": 0,
              "previous_cursor_str": "0"
            }
        """
        expected_list = [
            {u'username': u'Microsoft', u'firstname': u'Microsoft', u'userid': '74286565', u'followers_count': 3933376,
             'friends_count': 1054, 'messages_count': 7140,
             u'avatar': {u'48x48': u'http://pbs.twimg.com/profile_images/2535822544/secztwqh31xo8xydi4kq_normal.png'}},
        ]
        self._process_single_test(
            'get_friends',
            decoded_data,
            expected_list=expected_list,
        )

    def test_get_friends_loop(self):
        decoded_data = (
            '{"users":[{"id":74286565}],"next_cursor":100,"next_cursor_str":"100",'
            '"previous_cursor":0,"previous_cursor_str":"0"}'
        )

        self._process_single_test(
            'get_friends',
            decoded_data,
            expected_exception=ProviderCommunicationProxylibError,
        )

    def test_rate_limit_error(self):
        decoded_data = '{"errors":[{"message":"Rate limit exceeded","code":88}]}'
        self._process_single_test(
            'get_friends',
            decoded_data,
            expected_exception=ProviderRateLimitExceededProxylibError,
        )

    def test_get_profile_links(self):
        proxy = get_proxy(self.provider_code)
        links = proxy.get_profile_links('12345', 'some_user')
        eq_(links, [u'https://twitter.com/some_user'])

    def test_wall_post(self):
        # В реальности тут ад из десятка килобайтов данных, но они не используются.
        decoded_data = '{"id": 600279570412130304}'
        expected_dict = {
            'post_id': '600279570412130304',
        }
        self._process_single_test(
            'wall_post',
            decoded_data,
            kwargs={'link': 'http://yandex.ru'},
            expected_dict=expected_dict,
        )
