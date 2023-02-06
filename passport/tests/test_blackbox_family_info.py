# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
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
class TestBlackboxRequestGetFamilyInfo(BaseBlackboxRequestTestCase):
    FAMILY_ID = "f1"
    FAMILY_ADMIN = "70500"
    FAMILY_USERS = ["70500", "71001"]

    def test_family_info_basic_with_places(self):
        self.set_blackbox_response_value('''
            {
              "family": {
                "%s": {
                  "admin_uid": "%s",
                  "users": [
                    {
                      "uid": "70500",
                      "place": 0
                    },
                    {
                      "uid": "71001",
                      "place": 1
                    }
                  ]
                }
              }
            }
        ''' % (self.FAMILY_ID, self.FAMILY_ADMIN))

        response = self.blackbox.family_info(family_id=self.FAMILY_ID, get_place=True)
        exp_users = {
            int(uid): {'uid': uid, 'place': place}
            for place, uid in enumerate(self.FAMILY_USERS)
        }
        eq_(response, {
            'family_id': self.FAMILY_ID,
            'admin_uid': self.FAMILY_ADMIN,
            'users': exp_users,
        })

    def test_family_info_basic_without_places(self):
        self.set_blackbox_response_value('''
            {
              "family": {
                "%s": {
                  "admin_uid": "%s",
                  "users": [
                    {
                      "uid": "70500"
                    },
                    {
                      "uid": "71001"
                    }
                  ]
                }
              }
            }
        ''' % (self.FAMILY_ID, self.FAMILY_ADMIN))

        response = self.blackbox.family_info(family_id=self.FAMILY_ID)
        exp_users = {
            int(uid): {'uid': uid}
            for uid in self.FAMILY_USERS
        }
        eq_(response, {
            'family_id': self.FAMILY_ID,
            'admin_uid': self.FAMILY_ADMIN,
            'users': exp_users,
        })

    def test_family_info_nonexistent(self):
        self.set_blackbox_response_value('''
            {
              "family": {
                "%s": {
                }
              }
            }
        ''' % self.FAMILY_ID)

        response = self.blackbox.family_info(family_id=self.FAMILY_ID)
        ok_(response is None)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestGetFamilyInfoUrl(BaseBlackboxTestCase):
    FAMILY_ID = "f1"

    def test_family_info_url(self):
        request_info = Blackbox().build_family_info_request(
            family_id=self.FAMILY_ID,
            get_members_info='ehlo',
            get_place=False,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'method': 'family_info',
                'format': 'json',
                'family_id': self.FAMILY_ID,
                'get_members_info': 'ehlo',
            },
        )
