# -*- coding: utf-8 -*-

import json


class TestResponse(object):
    def __init__(self, response):
        self.original_response = response

    @property
    def status_code(self):
        return self.original_response.status_code

    @property
    def text(self):
        return self.original_response.data

    def json(self):
        return json.loads(self.original_response.data)


class TestClient(object):
    """
    Тестовый клиент для унификации интерфейсов Flask.TestClient и requests
    """

    def __init__(self, app):
        self.native_client = app.test_client()

    def prepare_args(self, *args, **kwargs):
        kwargs.pop('timeout', None)  # skip timeout
        kwargs.pop('verify', None)  # skip verify
        if 'json' in kwargs:
            if isinstance(kwargs['json'], dict):
                kwargs['content_type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['json'])
            kwargs.pop('json')
        if 'params' in kwargs:
            kwargs['query_string'] = kwargs['params']
            kwargs.pop('params')
        return args, kwargs

    def get(self, *args, **kwargs):
        args, kwargs = self.prepare_args(*args, **kwargs)
        return TestResponse(self.native_client.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        args, kwargs = self.prepare_args(*args, **kwargs)
        return TestResponse(self.native_client.post(*args, **kwargs))

    def delete(self, *args, **kwargs):
        args, kwargs = self.prepare_args(*args, **kwargs)
        return TestResponse(self.native_client.delete(*args, **kwargs))

    def put(self, *args, **kwargs):
        args, kwargs = self.prepare_args(*args, **kwargs)
        return TestResponse(self.native_client.put(*args, **kwargs))

    def patch(self, *args, **kwargs):
        args, kwargs = self.prepare_args(*args, **kwargs)
        return TestResponse(self.native_client.patch(*args, **kwargs))
