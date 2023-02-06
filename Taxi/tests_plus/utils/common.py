import json

HEADERS_MAP = {
    'yandex_uid': 'X-Yandex-UID',
    'remote_ip': 'X-Remote-IP',
    'request_language': 'X-Request-Language',
    'pass_flags': 'X-YaTaxi-Pass-Flags',
    'content_type': 'Content-type',
    'x_request_application': 'X-Request-Application',
}


class HttpRequest:
    _path = None
    _headers = None
    _body = None
    _params = None
    _func = None

    def __init__(self, method):
        self._func = method

    def path(self, path):
        self._path = path
        return self

    def headers(self, **kwargs):
        self._headers = self._headers or {}
        headers = {HEADERS_MAP.get(k) or k: v for k, v in kwargs.items()}
        self._headers.update(headers)
        return self

    def body(self, **kwargs):
        self._body = self._body or {}
        self._body.update(kwargs)
        return self

    def params(self, **kwargs):
        self._params = self._params or {}
        self._params.update(kwargs)
        return self

    async def perform(self):
        data = json.dumps(self._body) if self._body else None
        return await self._func(
            self._path, params=self._params, data=data, headers=self._headers,
        )
