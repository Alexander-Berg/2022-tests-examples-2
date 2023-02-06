import copy
import http

import pytest

import operation_calculations.geosubventions.storage as storage_lib

PARAMS = {
    'task_id': '5f9b08b19da21d52ed964470',
    'activity_points': 90,
    'begin_at': '2020-10-17T10:31:41',
    'close_all_current_rules': True,
    'end_at': '2020-10-18T10:31:41',
    'tariff_zones': ['moscow', 'dolgoprudny', 'himki'],
    'tariffs': ['econom'],
    'draft_polygons': {
        'prefix': '',
        'polygons': [
            {
                'polyId': 'mscmo_pol0',
                'name': 'mscmo_pol0',
                'draft_name': 'mscmo_pol0',
            },
            {
                'polyId': 'mscmo_pol2',
                'name': 'mscmo_pol2',
                'draft_name': 'mscmo_pol2',
            },
            {
                'polyId': 'mscmo_pol3',
                'name': 'mscmo_pol3',
                'draft_name': 'mscmo_pol3',
            },
            {
                'polyId': 'mscmo_pol5',
                'name': 'mscmo_pol5',
                'draft_name': 'mscmo_pol5',
            },
            {
                'polyId': 'mscmo_pol6',
                'name': 'mscmo_pol6',
                'draft_name': 'mscmo_pol6',
            },
        ],
    },
}


@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_multidraft_task_post(
        web_app_client, web_context,
):
    response = await web_app_client.post(
        '/v1/geosubventions/multidraft/tasks/',
        json=PARAMS,
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    task_id = result['task_id']

    storage = storage_lib.MultiDraftTasksStorage(web_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'].pop('with_experiments') is False
    assert task_data['params'] == PARAMS
    assert task_data['created_by'] == 'test_robot'
    assert task_data['referer'] == 'http://some.url'


@pytest.mark.parametrize(
    'extra_params,expected_result',
    (
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964474',
                'draft_polygons': {
                    'prefix': '',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'test_pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': '',
                        },
                    ],
                },
            },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for draft_name: \'\' length '
                        'must be greater than or equal to 1'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
        ),
        pytest.param(
            {'task_id': '5f9b08b19da21d52ed964470', 'ticket': '1234'},
            {'code': 'INCORRECT_TICKET', 'message': 'Incorrect ticket 1234'},
        ),
        pytest.param(
            {'task_id': 'unknown'},
            {
                'code': 'NotFound',
                'message': 'result for task unknown not found',
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_multidraft_task_post_bad_request(
        web_app_client, web_context, extra_params, expected_result,
):
    params = copy.deepcopy(PARAMS)
    params.update(extra_params)
    response = await web_app_client.post(
        '/v1/geosubventions/multidraft/tasks/',
        json=params,
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    result = await response.json()
    assert result == expected_result
