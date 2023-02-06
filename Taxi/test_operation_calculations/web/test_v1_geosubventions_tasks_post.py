import copy
import http
import json

from aiohttp import web
import bson
import pytest

from taxi import discovery

from test_operation_calculations import conftest


@pytest.mark.parametrize(
    'task_spec_key, expected_status',
    (
        pytest.param('a', http.HTTPStatus.OK),
        pytest.param('b', http.HTTPStatus.OK),
    ),
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
@pytest.mark.config(ATLAS_GEOSUBVENTIONS_MIN_GUARANTEE={'Россия': 5})
async def test_v1_geosubventions_tasks_status_post(
        web_app_client,
        task_spec_key,
        expected_status,
        caplog,
        mock_billing_subventions_x,
        response_mock,
        patch_aiohttp_session,
        open_file,
):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        req = request.json
        r_types = req['rule_types']
        rules = test_data['bsx_rules']
        return web.json_response(
            {
                'rules': [
                    rule for rule in rules if rule['rule_type'] in r_types
                ],
            },
        )

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url + '/v1/rules/select',
        'POST',
    )
    def _patch_request(method, url, **kwargs):
        r_types = kwargs['json']['types']
        rules = [
            rule
            for rule in test_data['billing_old_api']
            if rule['type'] in r_types
        ]
        return response_mock(json={'subventions': rules})

    task_spec = test_data['tasks'][task_spec_key]
    response = await web_app_client.post(
        f'/v1/geosubventions/tasks/',
        json=task_spec,
        headers={'X-Yandex-Login': 'test_robot'},
    )
    assert response.status == expected_status, await response.text()
    response = await response.json()
    task_id = response['task_id']
    assert bson.objectid.ObjectId.is_valid(task_id)
    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{task_id}/status/',
    )
    assert response.status == expected_status, await response.text()
    response = await response.json()
    assert response['status'] == 'STARTED'
    response = await web_app_client.get(f'/v1/geosubventions/tasks/{task_id}/')
    assert response.status == expected_status, await response.text()
    response = await response.json()
    expected_response = copy.deepcopy(task_spec)
    expected_response['task']['budget']['budget_scale'] = 1
    expected_response['task']['config_params'] = test_data['config_params']
    expected_response['task_id'] = task_id
    assert response == expected_response
