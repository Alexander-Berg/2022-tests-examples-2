# -*- coding: utf-8 -*-
from django.test import Client
from passport.backend.oauth.core.test.base_test_data import (
    TEST_HOST,
    TEST_REMOTE_ADDR,
)


class YandexAwareClient(Client):
    def __init__(self, *args, **kwargs):
        if 'REMOTE_ADDR' not in kwargs:
            kwargs['REMOTE_ADDR'] = TEST_REMOTE_ADDR
        super(YandexAwareClient, self).__init__(*args, **kwargs)

    def request(self, **request):
        if 'SERVER_NAME' not in request or request['SERVER_NAME'] == 'testserver':
            request['SERVER_NAME'] = TEST_HOST
        if 'HTTP_HOST' not in request:
            request['HTTP_HOST'] = TEST_HOST
        return super(YandexAwareClient, self).request(**request)
