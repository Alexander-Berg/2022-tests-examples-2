# -*- coding: utf-8 -*-

import logging
import allure
import pytest
from urlparse import urlparse

from common.client import MordaClient
from common.morda import Morda

logger = logging.getLogger(__name__)

@allure.feature('function_tests_stable')
@pytest.mark.parametrize(('tld', 'path', 'location', 'status_code'), [
    ['kz',  '/portal/video/', '/video', 302],
    ['ua',  '/portal/video/', '/video', 302],
    ['by',  '/portal/video/', '/video', 302],
    ['ru',  '/portal/video/', '/video', 302],
    ['com', '/portal/video/', None,     404],
])
def test_redirect(tld, path, location, status_code):
    client   = MordaClient()
    url = Morda.get_origin(no_prefix=True, domain=tld, env=client.env)

    response = client.request(url="{}{}".format(url, path), allow_redirects=False, allow_retry=False).send()
    headers = response.headers
    if location is None:
        assert 'Location' not in headers
        assert response.response.status_code == status_code
    else:
        assert response.response.status_code == status_code
        assert 'Location' in headers
        assert urlparse(headers['Location']).path == location, headers['Location']
