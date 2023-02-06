# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.consts import TEST_USER_IP1
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings_hosts,
)
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCheckIpParse(BaseBlackboxRequestTestCase):
    def test_ok(self):
        self.set_blackbox_response_value('{ "yandexip": true }')

        response = self.blackbox.check_ip(
            ip=TEST_USER_IP1,
        )
        assert response == {'yandexip': True}


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCheckIpRequest(BaseBlackboxTestCase):
    def test_ok(self):
        request_info = Blackbox().build_check_ip_request(
            ip=TEST_USER_IP1,
        )
        url = urlparse(request_info.url)
        assert url.netloc == 'localhost'

        check_all_url_params_match(
            request_info.url,
            {
                'format': 'json',
                'method': 'checkip',
                'ip': TEST_USER_IP1,
                'nets': 'yandexusers',
            },
        )
