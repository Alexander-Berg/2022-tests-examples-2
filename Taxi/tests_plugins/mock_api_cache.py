import re

import pytest


@pytest.fixture(name='api_cache', autouse=True)
def _api_cache(mockserver):
    class ApiCacheContext:
        def __init__(self):
            self.storage = {}
            # requests from the last check
            self.buffer = set()
            self.exception_if_not_found = False
            self.is_down = False

        def insert_key(self, key, value, ttl=None):
            self.storage[key] = Value(value, ttl)

        async def check_requests(self, key=None, get=False, put=False):
            if get:
                await _api_cache_handler.wait_call()
                if key:
                    request = (key, 'get')
                    assert request in self.buffer
                    self.buffer.remove(request)
            if put:
                await _api_cache_handler.wait_call()
                if key:
                    request = (key, 'put')
                    assert request in self.buffer
                    self.buffer.remove(request)
            # check no Unexpected events have come
            assert not self.buffer

    context = ApiCacheContext()

    class Value:
        def __init__(self, value, ttl=None):
            self.value = value
            self.ttl = ttl

    def extract_ttl(cache_control):
        if cache_control:
            result = re.search(r'max-age=(\d+)', cache_control)
            if result:
                return int(result.group(1))
        return None

    def get_source(request):
        HANDLER_PREFIX = '/api-cache/v1/cached-value/'
        if not request.path.startswith(HANDLER_PREFIX):
            raise RuntimeError(f'Request prefix is incorrect')
        if request.path[len(HANDLER_PREFIX) :].count('/'):
            raise RuntimeError(f'Do not use slashes in api-cache requests')
        return request.path[len(HANDLER_PREFIX) :]

    def get_value(context, request):
        context.buffer.add((request.args['key'], 'get'))
        key = get_source(request) + ':' + request.args['key']
        item = context.storage.get(key)
        if not item:
            if context.exception_if_not_found:
                raise RuntimeError('Failed to find value by key: %s' % key)
            return mockserver.make_response(status=404)
        return mockserver.make_response(
            response=item.value,
            headers={'Content-Type': 'application/octet-stream'},
        )

    def put_value(context, request):
        context.buffer.add((request.args['key'], 'put'))
        key = get_source(request) + ':' + request.args['key']
        assert request.headers['Content-Type'] == 'application/octet-stream'

        cache_control = request.headers.get('Cache-Control')
        ttl = extract_ttl(cache_control)
        context.storage[key] = Value(request.get_data(), ttl)
        return {}

    @mockserver.json_handler('/api-cache/v1/cached-value', prefix=True)
    def _api_cache_handler(request):
        if context.is_down:
            raise mockserver.TimeoutError()
        if request.method == 'GET':
            return get_value(context, request)
        if request.method == 'PUT':
            return put_value(context, request)
        raise RuntimeError('Unsupported method %s' % request.method)

    return context
