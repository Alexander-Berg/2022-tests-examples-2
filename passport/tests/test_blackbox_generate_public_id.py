# -*- coding: utf-8 -*-
from nose.tools import eq_
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
class TestBlackboxRequestGeneratePublicId(BaseBlackboxRequestTestCase):
    PUBLIC_ID = "f1"
    UID = '1234'

    def test_generate_public_id(self):
        self.set_blackbox_response_value('''
            {
              "public_id": "%s"
            }
        ''' % self.PUBLIC_ID)

        response = self.blackbox.generate_public_id(uid=self.UID)
        eq_(response, self.PUBLIC_ID)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestGeneratePublicIdUrl(BaseBlackboxTestCase):
    UID = '1234'

    def test_generate_public_id_url(self):
        request_info = Blackbox().build_generate_public_id_request(uid=self.UID)
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'method': 'generate_public_id',
                'format': 'json',
                'uid': self.UID,
            },
        )
