import copy
import dataclasses
import json
from typing import Dict
from typing import Tuple
from unittest import mock

import pytest

from taxi_buildagent.clients import clownductor
from tests.utils import repository
from tests.utils.examples import backend_py3
import upload_graphs


CLOWNDUCTOR_BASE_URL_MOCK = 'http://clownductor.taxi.tst.yandex.net'
CLOWNDUCTOR_UPLOAD_URL_MOCK = (
    f'{CLOWNDUCTOR_BASE_URL_MOCK}/v1/dashboard_configs/upload'
)
API_REQUESTS_FILENAME = (
    'clownductor_v1_dashboard_configs_upload_POST-{service}_{branch}.json'
)
_GENERATED_SERVICE_PATH_PREFIX = 'generated/services/{service}/'


@pytest.fixture(name='get_request_data_mock')
def _get_request_data_mock(load_json):
    obj = load_json('api_request_example.json')

    def _wrapper(
            project_name: str,
            service_name: str,
            branch_name: str,
            service_type: str,
    ):
        config = copy.deepcopy(obj)
        config['params']['project_name'] = project_name
        config['params']['service_name'] = service_name
        config['params']['branch_name'] = branch_name
        config['params']['service_type'] = service_type
        config['body']['hostnames'] = [
            f'{service_name}.taxi.yandex.net'
            if branch_name == 'stable'
            else f'{service_name}.taxi.tst.yandex.net',
        ]
        return config

    return _wrapper


@dataclasses.dataclass()
class ResponseMock:
    status_code: int
    retries: int = 1


@pytest.mark.parametrize('service_type', ['nanny', 'conductor'])
@pytest.mark.parametrize(
    'responses',
    [
        pytest.param(
            {
                ('test-service', 'stable', 'nanny'): ResponseMock(200),
                ('test-service', 'testing', 'nanny'): ResponseMock(200),
                ('test-service', 'stable', 'conductor'): ResponseMock(200),
                ('test-service', 'testing', 'conductor'): ResponseMock(200),
            },
            id='api_requests_success',
        ),
        pytest.param(
            {
                ('test-service', 'stable', 'nanny'): ResponseMock(400),
                ('test-service', 'testing', 'nanny'): ResponseMock(400),
                ('test-service', 'stable', 'conductor'): ResponseMock(400),
                ('test-service', 'testing', 'conductor'): ResponseMock(400),
            },
            id='api_error_for_service',
        ),
        pytest.param(
            {
                ('test-service', 'stable', 'nanny'): ResponseMock(400),
                ('test-service', 'testing', 'nanny'): ResponseMock(200),
                ('test-service', 'stable', 'conductor'): ResponseMock(400),
                ('test-service', 'testing', 'conductor'): ResponseMock(200),
            },
            id='api_error_for_branch',
        ),
        pytest.param(
            {
                ('test-service', 'stable', 'nanny'): ResponseMock(
                    409, clownductor.MAX_REQUESTS_RETRY,
                ),
                ('test-service', 'testing', 'nanny'): ResponseMock(
                    409, clownductor.MAX_REQUESTS_RETRY,
                ),
                ('test-service', 'stable', 'conductor'): ResponseMock(
                    409, clownductor.MAX_REQUESTS_RETRY,
                ),
                ('test-service', 'testing', 'conductor'): ResponseMock(
                    409, clownductor.MAX_REQUESTS_RETRY,
                ),
            },
            id='api_retries_exceeded',
        ),
    ],
)
def test_upload_graphs_to_api(
        tmpdir,
        monkeypatch,
        patch_requests,
        get_request_data_mock,
        service_type: str,
        responses: Dict[Tuple[str, str, str], ResponseMock],
):
    monkeypatch.setenv('CLOWNDUCTOR_TOKEN', 'secret')
    monkeypatch.setenv('CLOWNDUCTOR_URL', CLOWNDUCTOR_BASE_URL_MOCK)
    py3_repo = backend_py3.init(tmpdir.mkdir('backend-py3'))

    service = ('taxi-devops', 'test-service', service_type)
    branches = ['stable', 'testing']
    service_to_request_data_map = {}
    commits = []
    for branch in branches:
        project_name, service_name, service_type = service
        filename = API_REQUESTS_FILENAME.format(
            service=service_name, branch=branch,
        )
        config_request_data = get_request_data_mock(
            project_name=project_name,
            service_name=service_name,
            branch_name=branch,
            service_type=service_type,
        )
        service_to_request_data_map[
            (project_name, service_name, service_type, branch)
        ] = config_request_data

        commits.append(
            repository.Commit(
                'api requests',
                files=[
                    _GENERATED_SERVICE_PATH_PREFIX.format(service=service_name)
                    + f'/api_requests/{filename}',
                ],
                files_content=json.dumps(config_request_data),
            ),
        )

    repository.apply_commits(py3_repo, commits)

    @patch_requests(CLOWNDUCTOR_UPLOAD_URL_MOCK)
    def _dashboard_config_upload(*args, **kwargs):
        service_name = kwargs['params']['service_name']
        branch_name = kwargs['params']['branch_name']

        response = responses[(service_name, branch_name, service_type)]
        if not response.status_code == 200:
            body = json.dumps({'code': 'SOME_CODE', 'message': 'some message'})
            response_mock = patch_requests.response(
                status_code=response.status_code,
                content=bytes(body, 'utf-8'),
                text=body,
            )
        else:
            body = json.dumps(kwargs['json'])
            response_mock = patch_requests.response(
                status_code=response.status_code,
                content=bytes(body, 'utf-8'),
                text=body,
            )

        mocked = mock.MagicMock()
        mocked.retries.history = [i for i in range(response.retries - 1)]
        monkeypatch.setattr(response_mock, 'raw', mocked)
        return response_mock

    args = ['--repo', py3_repo.working_dir]
    upload_graphs.main(args)

    calls = _dashboard_config_upload.calls
    assert len(calls) == 2

    for call in _dashboard_config_upload.calls:
        project_name = call['kwargs']['params']['project_name']
        service_name = call['kwargs']['params']['service_name']
        branch_name = call['kwargs']['params']['branch_name']
        service_type = call['kwargs']['params']['service_type']

        service_info = (project_name, service_name, service_type, branch_name)
        assert (
            service_info in service_to_request_data_map
        ), service_to_request_data_map.keys()
        assert (
            call['kwargs']['json']
            == service_to_request_data_map[service_info]['body']
        )
        response = responses[(service_name, branch_name, service_type)]
        response.retries -= 1
        assert response.retries >= 0, f'Called more times than needed: {call}'
