# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# flake8: noqa

import pytest

from .integrator_v2_fixtures import mock_projects_response_data
from .integrator_v2_fixtures import support_explicit_mock
from .integrator_v2_fixtures import support_simple_mock


# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)

TVM_HEADER = 'X-Ya-Service-Ticket'

API_KEY_HEADER = 'Authentication'


@pytest.mark.config(
    SUPPORTAI_INTEGRATIONS_CACHE_CONFIG={'refresh_time': 1},
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [
            {
                'tvm_service_name': 'sample_client',
                'project_ids': ['sample_project'],
            },
        ],
    },
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'sample_client', 'dst': 'supportai-api'},
        {'src': 'supportai-api', 'dst': 'sample_client'},
    ],
    TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_response_codes(
        mock_projects_response_data,
        support_simple_mock,
        web_context,
        web_app_client,
):
    test_samples = [
        {
            'project_id': 4,
            'integrator_id': 'test_integration_1',
            'headers': {},
            'json': {},
            'response_status': 404,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_4',
            'headers': {},
            'json': {},
            'response_status': 404,
        },
        {
            'project_id': 1,
            'integrator_id': 'wrong_integration',
            'headers': {},
            'json': {},
            'response_status': 404,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_2',
            'headers': {},
            'json': {},
            'response_status': 403,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_2',
            'headers': {TVM_HEADER: TEST_SERVICE_TICKET},
            'json': {},
            'response_status': 400,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_1',
            'headers': {},
            'json': {},
            'response_status': 403,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_1',
            'headers': {TVM_HEADER: TEST_SERVICE_TICKET},
            'json': {},
            'response_status': 200,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'headers': {},
            'json': {},
            'response_status': 403,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'headers': {},
            'json': {'api_key': 'AsdadasdaQ23r'},
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/supportai-api/v2/external/{test_sample["integrator_id"]}'
            f'?project_id={test_sample["project_id"]}',
            headers=test_sample['headers'],
            json=test_sample['json'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.config(
    SUPPORTAI_INTEGRATIONS_CACHE_CONFIG={'refresh_time': 1},
    SUPPORTAI_API_INTERNAL_USERS={
        'users': [
            {
                'tvm_service_name': 'sample_client',
                'project_ids': ['sample_project'],
            },
        ],
    },
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'sample_client', 'dst': 'supportai-api'},
        {'src': 'supportai-api', 'dst': 'sample_client'},
    ],
    TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_response_data(
        mockserver,
        mock_projects_response_data,
        support_explicit_mock,
        web_context,
        web_app_client,
):
    test_samples = [
        {
            'project_id': 1,
            'integrator_id': 'test_integration_1',
            'headers': {TVM_HEADER: TEST_SERVICE_TICKET},
            'params': {},
            'json': {'action_slug': 'test_action_1'},
            'response_json': {'topic': 'topic', 'message': 'hello'},
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_1',
            'headers': {TVM_HEADER: TEST_SERVICE_TICKET},
            'params': {},
            'json': {},
            'response_json': {'response': 'some awesome mapping!!!'},
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'headers': {},
            'params': {},
            'json': {'api_key': 'AsdadasdaQ23r'},
            'response_json': {},
        },
        {
            'project_id': 2,
            'integrator_id': 'test_integration_4',
            'headers': {},
            'params': {
                'X-YaTaxi-API-Key': '321232131231',
                'signature': '0dba3fc5720e05a29a8debf4d735276b63426b83',
            },
            'json': {
                'action_id': 'test_action_6',
                'messages': [{'text': 'hello'}, {'text': 'world'}],
                'features': [
                    {'key': 'feature_1', 'value': 'value_1'},
                    {'key': 'feature_2', 'value': 'value_2'},
                ],
            },
            'response_json': {'message': 'hello', 'line': '12'},
        },
    ]

    @mockserver.json_handler('/callback-1')
    def callback_1_handler(request):
        assert request.method == 'GET'
        assert TVM_HEADER in request.headers

    @mockserver.json_handler('/callback-2')
    def callback_2_handler(request):
        assert request.method == 'POST'
        assert TVM_HEADER in request.headers

    @mockserver.json_handler('/callback-3')
    def callback_3_handler(request):
        assert request.method == 'DELETE'
        assert TVM_HEADER in request.headers
        assert request.json == {}

    @mockserver.json_handler('/callback-4')
    def callback_4_handler(request):
        assert request.method == 'DELETE'
        assert TVM_HEADER in request.headers
        assert request.json == {'message': 'Do not delete anything'}

    @mockserver.json_handler('/callback-5')
    def callback_5_handler(request):
        assert request.method == 'GET'
        assert TVM_HEADER in request.headers
        assert API_KEY_HEADER in request.headers
        assert request.headers[API_KEY_HEADER] == 'Bearer keeeeeeeey'

    @mockserver.json_handler('/callback-8')
    def callback_8_handler(request):
        assert request.method == 'GET'
        assert API_KEY_HEADER in request.headers
        assert request.headers[API_KEY_HEADER] == 'Bearer keykeykey'

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/supportai-api/v2/external/{test_sample["integrator_id"]}'
            f'?project_id={test_sample["project_id"]}',
            headers=test_sample['headers'],
            params=test_sample['params'],
            json=test_sample['json'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_json']

    assert callback_1_handler.times_called == 1
    assert callback_2_handler.times_called == 0
    assert callback_3_handler.times_called == 1
    assert callback_4_handler.times_called == 1
    assert callback_5_handler.times_called == 0
    assert callback_8_handler.times_called == 1
