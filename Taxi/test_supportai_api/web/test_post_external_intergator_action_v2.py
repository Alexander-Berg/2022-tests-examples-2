# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# flake8: noqa

import pytest

from .integrator_v2_fixtures import mock_projects_response_data
from .integrator_v2_fixtures import support_explicit_mock
from .integrator_v2_fixtures import support_simple_mock


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
            'action_id': 'some_action',
            'json': {},
            'response_status': 404,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_4',
            'action_id': 'some_action',
            'json': {},
            'response_status': 404,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'action_id': 'test_action_4',
            'json': {},
            'response_status': 403,
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'action_id': 'test_action_4',
            'json': {
                'api_key': 'AsdadasdaQ23r',
                'messages': [{'text': 'hello'}, {'text': 'world'}],
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/supportai-api/v2/external'
            f'/{test_sample["integrator_id"]}'
            f'/{test_sample["action_id"]}'
            f'?project_id={test_sample["project_id"]}',
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
            'integrator_id': 'test_integration_3',
            'action_id': 'test_action_4',
            'json': {
                'api_key': 'AsdadasdaQ23r',
                'messages': [{'text': 'hello'}, {'text': 'world'}],
            },
            'response_json': {},
        },
        {
            'project_id': 1,
            'integrator_id': 'test_integration_3',
            'action_id': 'test_action_5',
            'json': {'api_key': 'AsdadasdaQ23r'},
            'response_json': {'message': 'hello'},
        },
    ]

    @mockserver.json_handler('/callback-6')
    def callback_6_handler(request):
        assert request.method == 'GET'
        assert API_KEY_HEADER in request.headers
        assert request.headers[API_KEY_HEADER] == 'Bearer keeeeeeeey'

    @mockserver.json_handler('/callback-7')
    def callback_7_handler(request):
        assert request.method == 'POST'
        assert API_KEY_HEADER in request.headers
        assert request.headers[API_KEY_HEADER] == 'Bearer keeeeeeeey'
        assert request.json == {'data': '12'}

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/supportai-api/v2/external'
            f'/{test_sample["integrator_id"]}'
            f'/{test_sample["action_id"]}'
            f'?project_id={test_sample["project_id"]}',
            json=test_sample['json'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_json']

    assert callback_6_handler.times_called == 1
    assert callback_7_handler.times_called == 1
