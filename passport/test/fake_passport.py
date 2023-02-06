# -*- coding: utf-8 -*-

import re
from urlparse import urlparse

from passport.backend.core.builders.passport.faker.fake_passport import FakePassport as BaseFakePassport


account_options_re = re.compile('^/2/account/[^/]+/options/')


class FakePassport(BaseFakePassport):
    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        url_path = urlparse(url).path
        if url_path.startswith('/yasms/api/dropphone'):
            return 'yasms_api_drop_phone'
        if account_options_re.match(url_path):
            return 'account_options'
        return BaseFakePassport.parse_method_from_request(http_method, url, data, headers)
