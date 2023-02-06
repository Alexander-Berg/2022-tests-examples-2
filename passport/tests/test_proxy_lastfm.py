# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose.tools import eq_
from passport.backend.social.proxylib import get_proxy

from . import TestProxy


class TestProxyLastFm(TestProxy):
    provider_code = 'lf'

    def test_profile_1(self):
        decoded_data = """
            {
              "user": {
                "name": "Flidster",
                "realname": "Антон",
                "image": [
                  {
                    "#text": "",
                    "size": "small"
                  },
                  {
                    "#text": "",
                    "size": "medium"
                  },
                  {
                    "#text": "",
                    "size": "large"
                  },
                  {
                    "#text": "",
                    "size": "extralarge"
                  }
                ],
                "url": "http://www.last.fm/user/Flidster",
                "id": "56288542",
                "lang": "en",
                "country": "",
                "age": "24",
                "gender": "m",
                "subscriber": "0",
                "playcount": "512",
                "playlists": "1",
                "bootstrap": "0",
                "registered": {
                  "#text": "2013-10-24 11:05",
                  "unixtime": "1382612705"
                },
                "type": "user"
              }
            }
        """

        expected_dict = {u'username': u'Flidster', u'firstname': u'\u0410\u043d\u0442\u043e\u043d',
                         u'gender': u'm', u'userid': 'Flidster'}
        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_get_profile_links(self):
        proxy = get_proxy(self.provider_code)
        links = proxy.get_profile_links('12345', 'some_user')
        eq_(links, [u'http://www.last.fm/user/some_user'])
