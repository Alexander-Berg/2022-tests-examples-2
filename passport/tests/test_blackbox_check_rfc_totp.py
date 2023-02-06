# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    iterdiff,
    with_settings_hosts,
)
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCheckRfcTotpParse(BaseBlackboxRequestTestCase):
    def test_ok(self):
        self.set_blackbox_response_value('{ "status": "VALID", "time": 42 }')

        response = self.blackbox.check_rfc_totp(
            uid=123,
            totp='totp123',
        )
        eq_(
            response,
            dict(
                status='VALID',
                time=42,
            ),
        )


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCheckRfcTotpRequest(BaseBlackboxTestCase):
    def test_ok(self):
        request_info = Blackbox().build_check_rfc_totp_request(
            uid=123,
            totp='totp123',
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'format': 'json',
                'method': 'check_rfc_totp',
                'uid': '123',
                'totp': 'totp123',
            },
        )
