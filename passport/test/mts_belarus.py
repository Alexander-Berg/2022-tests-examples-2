# -*- coding: utf-8 -*-

import json

from furl import furl
from passport.backend.social.proxylib.repo.MtsBelarusRepo import MtsBelarusRepo

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


_DEFAULT_USER = {
    'id': '123456789000',
    'msisdn': '375299999999',
}


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(MtsBelarusRepo)

    def _request_to_method(self, request):
        url = furl(request['url'])
        path = str(url.path)
        if path == '/api/v1/info':
            return 'get_profile'


class MtsBelarusApi(object):
    """
    Модуль строит ответы ручек МТС.Беларусь API.
    """

    @classmethod
    def get_profile(cls, user={}):
        response = dict(_DEFAULT_USER, **user)
        return FakeResponse(json.dumps(response), 200)

    @classmethod
    def build_error(cls, http_status_code=403):
        return FakeResponse('', http_status_code)
