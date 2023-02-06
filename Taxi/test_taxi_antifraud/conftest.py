# pylint: disable=redefined-outer-name
import json
import os
import re
from typing import Any
from typing import Dict
import urllib.parse

import aiohttp
import pytest
import zeep

from taxi_antifraud.clients import fssp
import taxi_antifraud.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from taxi_antifraud.scoring.common import scoring_config as sc

pytest_plugins = ['taxi_antifraud.generated.service.pytest_plugins']

SPARK_LOGIN_TEST = 'Infernia'
SPARK_PASSWORD_TEST = 'Overkill'
SCORING_STUDIO_URL_TEST = 'scoringstudio.mock:/v1/scoring/request'
SCORING_STUDIO_API_KEY_TEST = '12345'
SUM_AND_SUBSTANCE_URL_TEST = 'sumsub.mock:/v1/scoring/request'
SUM_AND_SUBSTANCE_API_KEY_TEST = 'NJPFQPPUMERBRM'
SCORING_DRIVER_CALLBACK_URL_TEST = 'scoring_caller_mock:/v1/callback'


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'ANTIFRAUD_ANIMALS_PASSWORD': 'pass',
            'AFS_SPARK': {
                'login': SPARK_LOGIN_TEST,
                'password': SPARK_PASSWORD_TEST,
            },
            'AFS_FSSP': 'test_api_key',
            'AFS_SCORING_STUDIO': {'api_key': SCORING_STUDIO_API_KEY_TEST},
            'AFS_SUM_AND_SUBSTANCE': {
                'api_key': SUM_AND_SUBSTANCE_API_KEY_TEST,
            },
            'S3MDS_PAPERSPLEASE': {
                'url': 's3.mds.yandex.net',
                'bucket': 'testing_bucket',
                'access_key_id': 'key_to_access',
                'secret_key': 'very_secret',
            },
        },
    )
    return simple_secdist


@pytest.fixture(autouse=True)
def antifraud_monkeypatch_fixture(monkeypatch):
    monkeypatch.setattr(sc.ScoringConfig, 'NEED_LOAD_CODEGEN_CONTEXT', False)
    monkeypatch.setattr(sc.ScoringConfig, 'AFS_PARTNERS_SCORING', True)
    monkeypatch.setattr(sc.ScoringConfig, 'AFS_CORPS_SCORING', True)
    monkeypatch.setattr(zeep, 'Client', ZeepClientMock)
    monkeypatch.setattr(sc.ScoringConfig, 'AFS_FSSP_CHECK_STATUS_TIMEOUT', 3)
    monkeypatch.setattr(fssp, '_CHECK_STATUS_REQUEST_INTERVAL', 1)
    monkeypatch.setattr(
        sc.ScoringConfig,
        'AFS_SCORE_DRIVER',
        {
            'active_service': '',
            'callback_url': SCORING_DRIVER_CALLBACK_URL_TEST,
            'enabled': False,
            'services': {},
        },
    )


class ZeepServiceMock:
    # pylint: disable=invalid-name
    async def Authmethod(self, Login=None, Password=None):
        assert Login == SPARK_LOGIN_TEST
        assert Password == SPARK_PASSWORD_TEST
        return 'True'

    # pylint: disable=invalid-name
    async def End(self):
        pass

    # pylint: disable=invalid-name
    async def GetCompanyExtendedReport(self, inn=None):
        # pylint: disable=unsubscriptable-object
        return self._responses[str(inn)]['GetCompanyExtendedReport']

    # pylint: disable=invalid-name
    async def GetCompanySparkRisksReportXML(self, inn=None):
        # pylint: disable=unsubscriptable-object
        return self._responses[str(inn)]['GetCompanySparkRisksReportXML']

    # pylint: disable=invalid-name
    async def GetEntrepreneurShortReport(self, inn=None):
        # pylint: disable=unsubscriptable-object
        return self._responses[str(inn)]['GetEntrepreneurShortReport']

    @classmethod
    def set_responses(cls, load, filename):
        cls._responses = load(filename + os.path.extsep + 'json')
        cls._glue_strings(cls._responses)

    @classmethod
    def _glue_strings(cls, json_data):
        for key, val in json_data.items():
            if isinstance(val, list):
                need_to_glue = bool(val)
                for it in val:
                    if not isinstance(it, str):
                        need_to_glue = False
                    if isinstance(it, dict):
                        cls._glue_strings(it)
                if need_to_glue:
                    json_data[key] = ''.join(line.lstrip() for line in val)
            elif isinstance(val, dict):
                cls._glue_strings(val)

    _responses = None


class ZeepClientMock:
    def __init__(self, wsdl_file, transport=None):
        assert os.path.isfile(wsdl_file)
        self.service = ZeepServiceMock()


@pytest.fixture
def prepare_zeep_mock_spark(load_json):
    ZeepServiceMock.set_responses(load_json, 'spark_responses')


@pytest.fixture
def prepare_zeep_mock_for_fssp(load_json):
    ZeepServiceMock.set_responses(load_json, 'spark_responses_for_fssp')


class ScoringServiceMock:
    @classmethod
    def request(cls, base_url: str, method, url, response_mock, **kwargs):
        scoring_service_type = sc.ScoringConfig.AFS_SCORE_DRIVER[
            'active_service'
        ]
        services = sc.ScoringConfig.AFS_SCORE_DRIVER['services']  # type: Any
        scoring_service_url = services[str(scoring_service_type)]['url']

        mock = cls._mocks[base_url]

        if (
                mock['headers']
                and ('X-Api-Key' in mock['headers'])
                and (
                    'headers' not in kwargs
                    or kwargs['headers']['X-Api-Key']
                    != mock['headers']['X-Api-Key']
                )
        ):
            return response_mock(status=401)

        if mock['params'] and 'key' in mock['params']:
            parts = urllib.parse.urlparse(url)
            if parts.query:
                query = urllib.parse.parse_qs(parts.query)
                if 'key' not in query or (
                        query['key'][0] != mock['params']['key']
                ):
                    return response_mock(status=401)

        status = 500
        response_data = None
        if mock['data']:
            if method == 'post':
                status, response_data = cls._mock_post(
                    mock, scoring_service_url, url, kwargs.get('json'),
                )
            elif method == 'get':
                status, response_data = cls._mock_get(
                    mock, scoring_service_url, url,
                )
            else:
                status = 404
        result = response_mock(status=status, text=json.dumps(response_data))
        return result

    @staticmethod
    def _mock_post(mock, scoring_service_url, url, request_json):
        responses = mock['data']['requests']
        status = 404
        response_data = None

        if url.startswith(scoring_service_url):
            if request_json:
                request_json_string = json.dumps(
                    request_json, sort_keys=True, ensure_ascii=False,
                )
                if request_json_string in responses:
                    response_data = responses[request_json_string]
                else:
                    raise RuntimeError(
                        'ScoringServiceMock '
                        'failed for post request: "{}"'.format(
                            request_json_string.replace('"', '\\"'),
                        ),
                    )
                status = 200
        return status, response_data

    @classmethod
    def _mock_get(cls, mock, scoring_service_url, url):
        print('_mock_get {},{}'.format(scoring_service_url, url))
        status = 404
        response_data = None
        if url.startswith(scoring_service_url + '/'):
            responses = mock['data']['results']
            url_payload = re.split('[/?]', url[len(scoring_service_url) + 1 :])
            request_id = url_payload[0]
            if len(url_payload) > 1 and not (
                    url_payload[1] == mock['get_status_suffix']
            ):
                status = 404
            elif request_id in responses:
                # count GET requests for each id, per service
                service_request_id = '{}/{}'.format(
                    scoring_service_url, request_id,
                )
                request_order = cls._result_requests_by_id.get(
                    service_request_id, 0,
                )
                cls._result_requests_by_id[service_request_id] = (
                    request_order + 1
                )

                # return results in order
                response_sequence = responses[request_id]
                response_data = response_sequence[
                    min(request_order, len(response_sequence) - 1)
                ]

                if 'error' in response_data:
                    # we are not supposed to hit this if all cached
                    # reports are properly found in mock DB
                    status = response_data['error']
                    raise RuntimeError(
                        'ScoringStudio mock '
                        'intentional failure for requestID {}'.format(
                            request_id,
                        ),
                    )
            else:
                raise RuntimeError(
                    'ScoringServiceMock '
                    'failed for get request: {}'.format(request_id),
                )
            status = 200

        return status, response_data

    @classmethod
    def init_mocks(cls, load):
        cls._mocks[SCORING_STUDIO_URL_TEST]['data'] = load(
            'scoring_studio_responses' + os.path.extsep + 'json',
        )
        cls._mocks[SUM_AND_SUBSTANCE_URL_TEST]['data'] = load(
            'sum_and_substance_responses' + os.path.extsep + 'json',
        )

    _mocks: Dict[str, Dict[str, Any]] = {
        SCORING_STUDIO_URL_TEST: {
            'headers': {'X-Api-Key': SCORING_STUDIO_API_KEY_TEST},
            'params': {'key': ''},
            'data': {},
            'get_status_suffix': '',
        },
        SUM_AND_SUBSTANCE_URL_TEST: {
            'headers': {},
            'params': {'key': SUM_AND_SUBSTANCE_API_KEY_TEST},
            'data': {},
            'get_status_suffix': 'status',
        },
    }

    _responses = None
    _result_requests_by_id: dict = {}


@pytest.fixture
def prepare_scoring_services_mock(
        load_json, patch_aiohttp_session, response_mock,
):
    # pylint: disable=unused-variable
    @patch_aiohttp_session(SCORING_STUDIO_URL_TEST)
    def patch_request1(method, url, **kwargs):
        return ScoringServiceMock.request(
            SCORING_STUDIO_URL_TEST, method, url, response_mock, **kwargs,
        )

    # pylint: disable=unused-variable
    @patch_aiohttp_session(SUM_AND_SUBSTANCE_URL_TEST)
    def patch_request2(method, url, **kwargs):
        return ScoringServiceMock.request(
            SUM_AND_SUBSTANCE_URL_TEST, method, url, response_mock, **kwargs,
        )

    ScoringServiceMock.init_mocks(load_json)


class ScoringCallbackMock:
    @classmethod
    def request(cls, method, url, response_mock, **kwargs):
        callback_url = sc.ScoringConfig.AFS_SCORE_DRIVER['callback_url']

        if method == 'post' and url == callback_url:
            cls._call_count += 1
            status = 200
        else:
            status = 404

        return response_mock(status=status)

    @classmethod
    def get_call_count(cls):
        return cls._call_count

    @classmethod
    def reset_call_count(cls):
        cls._call_count = 0

    _call_count = 0


@pytest.fixture
def prepare_scoring_callback_mock(
        load_json, patch_aiohttp_session, response_mock,
):
    callback_url = SCORING_DRIVER_CALLBACK_URL_TEST

    # pylint: disable=unused-variable
    @patch_aiohttp_session(callback_url)
    def patch_request(method, url, **kwargs):
        return ScoringCallbackMock.request(
            method, url, response_mock, **kwargs,
        )

    ScoringCallbackMock.reset_call_count()


class RequestMock:
    def __init__(self, url, params):
        self._url = url
        self._params = params
        response = self.get_response(self._url, self._params)
        self.content = response.get('response', None)
        self.status = response.get('code', None)

    async def text(self):
        return self.content

    async def json(self):
        return self.content

    @classmethod
    def set_responses(cls, load, filename):
        cls._responses = load(filename + os.path.extsep + 'json')

    @classmethod
    def get_response(cls, url, params):
        # pylint: disable=unsubscriptable-object
        info = cls._responses[url]
        for param in params:
            info = info.get(params[param], info)

        return info

    _responses = None


class RequestContextManagerMock:
    def __init__(self, request):
        self._request = request

    async def __aenter__(self):
        return self._request

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def prepare_mock_aiohttp_for_fssp(monkeypatch, load_json):
    RequestMock.set_responses(load_json, 'fssp_server_responses')

    def get(self, url, *, allow_redirects=True, **kwargs):
        return RequestContextManagerMock(
            RequestMock(url, kwargs.get('params', [])),
        )

    monkeypatch.setattr(aiohttp.client.ClientSession, 'get', get)
