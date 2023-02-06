import json
import typing
import urllib.parse

import aiohttp.web


class BaseError(Exception):
    pass


class MockedError(BaseError):
    """Base class for mockserver mocked errors."""

    error_code = 'unknown'


class TimeoutError(MockedError):  # pylint: disable=redefined-builtin
    error_code = 'timeout'


class NetworkError(MockedError):
    error_code = 'network'


class HttpResponseError(BaseError):
    def __init__(self, *, url: str, status: int):
        self.url = url
        self.status = status
        super().__init__(f'status={self.status}, url=\'{self.url}\'')


class Request:
    """ Adapts aiohttp.web.Request to mimic a frequently used subset of
    werkzeug.Request interface. `data` property is not supported,
    use get_data() instead.
    """

    def __init__(self, request: aiohttp.web.Request, data: bytes):
        self._request = request
        self._data: bytes = data
        self._json: object = None
        self._form: typing.Optional[typing.Dict[str, str]] = None

    @property
    def method(self) -> str:
        return self._request.method

    @property
    def url(self) -> str:
        return str(self._request.url)

    @property
    def path(self) -> str:
        return self._request.path

    # For backward compatibility with code using aiohttp.web.Request
    @property
    def path_qs(self) -> str:
        return self._request.raw_path

    @property
    def query_string(self) -> bytes:
        path_and_query = self._request.raw_path.split('?')
        if len(path_and_query) < 2:
            return b''
        return path_and_query[1].encode()

    @property
    def headers(self):
        return self._request.headers

    @property
    def content_type(self):
        return self._request.content_type

    def get_data(self) -> bytes:
        return self._data

    @property
    def form(self):
        if self._form is None:
            if self._request.content_type in (
                    '',
                    'application/x-www-form-urlencoded',
            ):
                charset = self._request.charset or 'utf-8'
                items = urllib.parse.parse_qsl(
                    self._data.rstrip().decode(charset),
                    keep_blank_values=True,
                    encoding=charset,
                )
                self._form = {key: value for key, value in items}
            else:
                self._form = {}

        return self._form

    @property
    def json(self) -> typing.Any:
        if self._json is None:
            bytes_body = self.get_data()
            encoding = self._request.charset or 'utf-8'
            self._json = json.loads(bytes_body, encoding=encoding)
        return self._json

    @property
    def cookies(self) -> typing.Mapping[str, str]:
        return self._request.cookies

    @property
    def args(self):
        return self._request.query

    # For backward compatibility with code using aiohttp.web.Request
    @property
    def query(self):
        return self._request.query


class _NoValue:
    pass


async def wrap_request(request: aiohttp.web.Request):
    if request.headers.get('expect') == '100-continue':
        await request.writer.write(b'HTTP/1.1 100 Continue\r\n\r\n')
        await request.writer.drain()
    data = await request.content.read()
    return Request(request, data)


class ClientResponse:
    def __init__(self, response: aiohttp.ClientResponse, content: bytes):
        self._response = response
        self._content: bytes = content
        self._text: typing.Optional[str] = None

    @property
    def status_code(self) -> int:
        return self._response.status

    # For backward compatibility with code using async ClientResponse
    @property
    def status(self) -> int:
        return self._response.status

    @property
    def reason(self) -> typing.Optional[str]:
        return self._response.reason

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def text(self) -> str:
        if self._text is None:
            encoding = self._response.get_encoding()
            self._text = str(self._content, encoding)
        return self._text

    def json(self) -> typing.Any:
        encoding = self._response.get_encoding()
        return json.loads(self._content, encoding=encoding)

    @property
    def headers(self):
        return self._response.headers

    @property
    def content_type(self):
        return self._response.content_type

    @property
    def encoding(self):
        return self._response.get_encoding()

    @property
    def cookies(self):
        return self._response.cookies

    def raise_for_status(self) -> None:
        if self._response.status < 400:
            return
        self._response.release()
        raise HttpResponseError(
            url=self._response.request_info.url, status=self._response.status,
        )


async def wrap_client_response(response: aiohttp.ClientResponse):
    content = await response.read()
    wrapped = ClientResponse(response, content)
    return wrapped


def make_response(
        response: typing.Union[str, bytes, bytearray] = None,
        status: int = 200,
        headers: typing.Mapping[str, str] = None,
        content_type: typing.Optional[str] = None,
        charset: typing.Optional[str] = None,
        *,
        json=_NoValue,
) -> aiohttp.web.Response:
    if json is not _NoValue:
        response = _json_response(json)
        if content_type is None:
            content_type = 'application/json'
    if isinstance(response, (bytes, bytearray)):
        return aiohttp.web.Response(
            body=response,
            status=status,
            headers=headers,
            content_type=content_type,
            charset=charset,
        )
    if isinstance(response, str):
        return aiohttp.web.Response(
            text=response,
            status=status,
            headers=headers,
            content_type=content_type,
            charset=charset,
        )
    if response is None:
        return aiohttp.web.Response(
            headers=headers,
            status=status,
            content_type=content_type,
            charset=charset,
        )
    raise RuntimeError(f'Unsupported response {response!r} given')


def _json_response(data: typing.Any) -> bytes:
    text = json.dumps(data, ensure_ascii=False)
    return text.encode('utf-8')
