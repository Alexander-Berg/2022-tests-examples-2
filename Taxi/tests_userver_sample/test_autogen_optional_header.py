from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional


URL = 'autogen/optional-header/{type}/{schema}'
URL_TYPES = ['inplace', 'ref', 'strong-typedef']
URL_SCHEMAS = ['openapi-3-0']
PARAMS_RESPONSE_CODE = [200, 400]

X_TEST_HEADER = 'X-Test-Header'
X_TEST_OPTIONAL_HEADER = 'X-Test-Optional-Header'

HEADERS = {X_TEST_HEADER, X_TEST_OPTIONAL_HEADER}

ASSERT_ERROR = (
    '\n\n'
    '###############################################################\n'
    'Error with request\n'
    'Url: {url}\n'
    'Headers: {headers}\n'
    'Params: {params}\n'
    'Message: {msg}\n'
    'Response: {response}\n'
    '###############################################################\n'
    '\n'
)


class Case:
    def __init__(
            self,
            request_url: str,
            request_headers: Dict[str, str],
            request_params: Dict[str, Any],
            response_code: int,
            response_headers: Dict[str, str],
            response_body: Dict[Any, Any],
    ) -> None:
        self.request_url = request_url
        self.request_headers = request_headers
        self.request_params = request_params

        self.response_code = response_code
        self.response_headers = response_headers
        self.response_body = response_body

    async def do_test(self, client, mockserver, mock_times_called=1) -> None:
        @mockserver.json_handler(f'userver-sample/{self.request_url}')
        def mock_view(request):
            return mockserver.make_response(
                headers={
                    h: request.headers[h]
                    for h in HEADERS
                    if h in request.headers
                },
                json={},
            )

        response = await client.get(
            self.request_url,
            headers=self.request_headers,
            params=self.request_params,
        )

        self._assert_response_code(response)
        self._assert_valid_headers(response)
        self._assert_invalid_headers(response)
        self._assert_body(response)
        assert mock_view.times_called == mock_times_called, self._assert_msg(
            response,
            f'Unexpected mock times called: {mock_view.times_called}',
        )

    def _assert_msg(self, response, msg: str) -> str:
        return ASSERT_ERROR.format(
            url=self.request_url,
            headers=self.request_headers,
            params=self.request_params,
            msg=msg,
            response=response.text,
        )

    def _assert_response_code(self, response) -> None:
        assert response.status_code == self.response_code, self._assert_msg(
            response, 'Unexpected response code',
        )

    def _assert_valid_headers(self, response) -> None:
        for header_key, header_value in self.response_headers.items():
            assert header_key in response.headers, self._assert_msg(
                response, f'Header "{header_key}" must be in response',
            )
            assert response.headers[header_key] == header_value, (
                self._assert_msg(
                    response,
                    f'Unexpected header "{header_key}" value in response',
                )
            )

    def _assert_invalid_headers(self, response) -> None:
        for header_key in HEADERS.difference(self.response_headers.keys()):
            assert header_key not in response.headers, self._assert_msg(
                response, f'Header "{header_key}" must not be in response',
            )

    def _assert_body(self, response) -> None:
        assert response.json() == self.response_body, self._assert_msg(
            response, 'Unexpected response body',
        )


def iterate_all_cases(
        request_headers: Dict[str, str],
        response_code: Optional[int] = None,
        response_headers: Optional[Dict[str, str]] = None,
        response_body: Optional[Dict[Any, Any]] = None,
) -> Iterable[Case]:
    def _get_response_code(_code: int) -> int:
        if response_code is not None:
            return response_code
        return _code

    if response_headers is None:
        response_headers = request_headers

    if response_body is None:
        response_body = {}

    for url_type in URL_TYPES:
        for url_schema in URL_SCHEMAS:
            url = URL.format(type=url_type, schema=url_schema)
            for param_response_code in PARAMS_RESPONSE_CODE:
                yield Case(
                    request_url=url,
                    request_headers=request_headers,
                    request_params={'response_code': param_response_code},
                    response_code=_get_response_code(param_response_code),
                    response_headers=response_headers,
                    response_body=response_body,
                )


async def test_headers_exist(taxi_userver_sample, mockserver):
    headers = {X_TEST_HEADER: 'qwe', X_TEST_OPTIONAL_HEADER: 'rty'}
    for case in iterate_all_cases(headers):
        await case.do_test(taxi_userver_sample, mockserver)


async def test_optional_headers_not_exist(taxi_userver_sample, mockserver):
    headers = {X_TEST_HEADER: 'qwe'}
    for case in iterate_all_cases(headers):
        await case.do_test(taxi_userver_sample, mockserver)


async def test_required_headers_not_exist(taxi_userver_sample, mockserver):
    headers = {X_TEST_OPTIONAL_HEADER: 'rty'}
    response_body = {
        'code': '400',
        'message': 'Missing X-Test-Header in header',
    }
    for case in iterate_all_cases(headers, 400, {}, response_body):
        await case.do_test(taxi_userver_sample, mockserver, 0)
