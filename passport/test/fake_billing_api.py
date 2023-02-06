# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from json import dumps as json_dumps
from re import compile as re_compile
from urlparse import urlparse

from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.social.common.builders.billing import BillingApi


INVALIDATE_ACCOUNT_BINDINGS_RE = re_compile(r'/trust-payments/v2/passport/\d+/invalidate$')


def billing_api_invalidate_account_bindings_response(status='success'):
    return json_dumps({'status': status, 'status_code': 'invalidated'})


def billing_api_fail_response(status_code=''):
    return json_dumps({'status': 'error', 'status_code': status_code})


class FakeBillingApi(BaseFakeBuilder):
    def __init__(self):
        super(FakeBillingApi, self).__init__(BillingApi)

    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        url_path = urlparse(url).path
        if INVALIDATE_ACCOUNT_BINDINGS_RE.match(url_path):
            return 'invalidate_account_bindings'
