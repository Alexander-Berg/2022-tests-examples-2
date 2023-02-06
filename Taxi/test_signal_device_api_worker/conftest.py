# pylint: disable=redefined-outer-name
import typing

import pytest

import signal_device_api_worker.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['signal_device_api_worker.generated.service.pytest_plugins']

SETTINGS_OVERRIDE = {
    'SIGNAL_DEVICE_API_MDS_S3': {
        'url': 'https://s3.mock.net',
        'bucket': 'sda-videos',
        'access_key_id': 'access_key',
        'secret_key': '53cr37_k3y',
    },
}

STATUS_COMPLETED = 'COMPLETED'
STATUS_CANCELLED = 'CANCELLED'
STATUS_ERROR = 'ERROR'


class MockedTable:
    def __init__(
            self,
            data: typing.List[typing.List[typing.Any]],
            names: typing.Optional[typing.List[str]] = None,
            types: typing.Optional[typing.List[str]] = None,
    ):
        self._data: typing.List[typing.List[typing.Any]] = data
        self._names: typing.List[str] = names or []
        self._types: typing.List[str] = types or []

    def fetch_full_data(self):
        pass

    @property
    def rows(self) -> typing.List[typing.List[typing.Any]]:
        return self._data


class MockedResult:
    def __init__(self, status: str, data: typing.List[MockedTable]):
        self._status = status
        self._data = data

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_success(self) -> bool:
        return self._status == STATUS_COMPLETED

    @property
    def errors(self) -> typing.List[Exception]:
        return (
            [Exception('The nastiest error')]
            if self.status == STATUS_ERROR
            else []
        )

    def __iter__(self) -> typing.Iterator:
        yield from self._data


class MockedRequest:
    def __init__(self, result: MockedResult):
        self._result = result

    def run(self):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    def get_results(self, *args, **kwargs):
        return self._result


@pytest.fixture
def mocked_yql(patch):
    requests = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        nonlocal requests
        return requests.pop(0)

    @patch('yql.client.operation.YqlOperationStatusRequest')
    def yql_operation_status_request(operation_id):
        class YQLRequest:
            status = 'COMPLETED'
            json = {}

            def run(self):
                pass

        return YQLRequest()

    return requests


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist


MDS_HOST_INTERNAL = 'https://s3.mock.net'
S3_RESPONSE_HEADERS = {
    'server': 'nginx',
    'date': 'Tue, 10 Mar 2020 13:32:47 GMT',
}


@pytest.fixture(autouse=True)
def mock_s3_delete_objects(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(MDS_HOST_INTERNAL, 'POST')
    def _patch_request_post(method, url, headers, **kwargs):
        s3_response_headers = S3_RESPONSE_HEADERS
        response = response_mock(headers=s3_response_headers)
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        return response
