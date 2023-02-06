# -*- coding: utf-8 -*-

from urlparse import (
    parse_qs,
    urlparse,
)

from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response  # noqa


class FakeBlackbox(BaseFakeBuilder):
    def __init__(self):
        super(FakeBlackbox, self).__init__(Blackbox)
        self.set_blackbox_response_value = self.set_response_value
        self.set_blackbox_response_side_effect = self.set_response_side_effect

    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if path == 'blackbox':
            query = parsed.query
            if http_method != 'POST':
                method = parse_qs(query)['method'][0]
            else:
                method = data['method']
        else:
            method = 'lrandoms_' + path
        return method
