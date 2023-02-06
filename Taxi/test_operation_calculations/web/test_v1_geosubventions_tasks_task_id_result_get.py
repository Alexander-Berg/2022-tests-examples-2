import http
from typing import Any
from typing import Dict

from aiohttp import web
import pytest

DEFAULT_RESTRICTIONS_CONF: Dict[str, Any] = {
    'max_guarantee': None,
    'max_polygon_edges': None,
    'max_subvention_area_ratio': 0.7,
    'max_total_intervals': 4,
    'max_subgmv_critical': 200,
    'max_subgmv_critical_logistics': 250,
    'max_subgmv_warning': 100,
    'max_subgmv_warning_logistics': 150,
}

DEFAULT_RESTRICTIONS: Dict[str, Any] = {
    'max_guarantee': None,
    'max_polygon_edges': None,
    'max_subvention_area_ratio': 0.7,
    'min_guarantee': None,
    'max_subgmv_critical': 200,
    'max_subgmv_critical_logistics': 250,
    'max_subgmv_warning': 100,
    'max_subgmv_warning_logistics': 150,
}
DEFAULT_WARNINGS: Dict[str, Any] = {
    'draft_rules': [],
    'general': [],
    'polygons': [],
    'rush_hours': [],
}


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '5f9b08b19da21d52ed964473',
            http.HTTPStatus.OK,
            {
                'task_id': '5f9b08b19da21d52ed964473',
                'rush_hours': {
                    '0': [
                        {
                            'start_dayofweek': 2,
                            'start_time': '00:00',
                            'end_dayofweek': 2,
                            'end_time': '01:00',
                        },
                        {
                            'start_dayofweek': 5,
                            'start_time': '00:00',
                            'end_dayofweek': 5,
                            'end_time': '01:00',
                        },
                        {
                            'start_dayofweek': 6,
                            'start_time': '00:00',
                            'end_dayofweek': 6,
                            'end_time': '01:00',
                        },
                        {
                            'start_dayofweek': 6,
                            'start_time': '02:00',
                            'end_dayofweek': 6,
                            'end_time': '03:00',
                        },
                        {
                            'start_dayofweek': 5,
                            'start_time': '23:00',
                            'end_dayofweek': 6,
                            'end_time': '00:00',
                        },
                    ],
                    '2': [
                        {
                            'start_dayofweek': 0,
                            'start_time': '07:00',
                            'end_dayofweek': 0,
                            'end_time': '08:00',
                        },
                        {
                            'start_dayofweek': 6,
                            'start_time': '09:00',
                            'end_dayofweek': 6,
                            'end_time': '10:00',
                        },
                        {
                            'start_dayofweek': 5,
                            'start_time': '10:00',
                            'end_dayofweek': 5,
                            'end_time': '11:00',
                        },
                    ],
                },
                'polygons': [
                    {
                        'id': '5fb38a175e48dae578953b08_pol0',
                        'type': 'Feature',
                        'properties': {'name': 'pol0'},
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [
                                [
                                    [50.28081572113459, 53.24089465235615],
                                    [50.28729095173748, 53.23952285175096],
                                    [50.2884903, 53.2391425],
                                    [50.28081572113459, 53.24089465235615],
                                ],
                            ],
                        },
                    },
                    {
                        'id': '5fb38a175e48dae578953b08_pol1',
                        'type': 'Feature',
                        'properties': {'name': 'pol1'},
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [
                                [
                                    [50.26784131007092, 53.25091179801678],
                                    [50.26857345576475, 53.24658996980415],
                                    [50.262743, 53.2340709996],
                                    [50.26784131007092, 53.25091179801678],
                                ],
                            ],
                        },
                    },
                    {
                        'id': '5fb38a175e48dae578953b08_pol3',
                        'type': 'Feature',
                        'properties': {'name': 'pol3'},
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [
                                [
                                    [50.077633, 53.178471],
                                    [50.07736569338627, 53.17848700187584],
                                    [50.076286, 53.178841],
                                    [50.077633, 53.178471],
                                ],
                            ],
                        },
                    },
                ],
                'draft_rules': [
                    {
                        'categories': ['econom'],
                        'rule_sum': 205,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol0'],
                        'interval': {
                            'start_dayofweek': 2,
                            'start_time': '00:00',
                            'end_dayofweek': 2,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 180,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol1'],
                        'interval': {
                            'start_dayofweek': 2,
                            'start_time': '00:00',
                            'end_dayofweek': 2,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 165,
                        'rule_type': 'guarantee',
                        'geoareas': [
                            '5fb38a175e48dae578953b08_pol0',
                            '5fb38a175e48dae578953b08_pol1',
                        ],
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '00:00',
                            'end_dayofweek': 5,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 150,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol0'],
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '00:00',
                            'end_dayofweek': 6,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 185,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol1'],
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '00:00',
                            'end_dayofweek': 6,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 180,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol0'],
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '02:00',
                            'end_dayofweek': 6,
                            'end_time': '03:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 160,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol1'],
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '02:00',
                            'end_dayofweek': 6,
                            'end_time': '03:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 140,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol0'],
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '23:00',
                            'end_dayofweek': 6,
                            'end_time': '00:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 160,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol1'],
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '23:00',
                            'end_dayofweek': 6,
                            'end_time': '00:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 190,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol3'],
                        'interval': {
                            'start_dayofweek': 0,
                            'start_time': '07:00',
                            'end_dayofweek': 0,
                            'end_time': '08:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 130,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol3'],
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '09:00',
                            'end_dayofweek': 6,
                            'end_time': '10:00',
                        },
                    },
                    {
                        'categories': ['econom'],
                        'rule_sum': 135,
                        'rule_type': 'guarantee',
                        'geoareas': ['5fb38a175e48dae578953b08_pol3'],
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '10:00',
                            'end_dayofweek': 5,
                            'end_time': '11:00',
                        },
                    },
                ],
                'budget': [
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol0': {
                                'subv_cost': 25415.257562500003,
                                'subv_cost_wo_surge': 62763.94302333359,
                                'orders_cnt': 765.7205,
                                'unique_drivers': 1.057625,
                            },
                            '5fb38a175e48dae578953b08_pol1': {
                                'subv_cost': 12100.8164375,
                                'subv_cost_wo_surge': 26588.15474967497,
                                'orders_cnt': 429.9245625,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 2,
                            'start_time': '00:00',
                            'end_dayofweek': 2,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol0': {
                                'subv_cost': 43272.726875,
                                'subv_cost_wo_surge': 85528.8611426557,
                                'orders_cnt': 1577.4476875,
                                'unique_drivers': 1.057625,
                            },
                            '5fb38a175e48dae578953b08_pol1': {
                                'subv_cost': 21265.1370625,
                                'subv_cost_wo_surge': 42723.55697123204,
                                'orders_cnt': 850.8593125,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '00:00',
                            'end_dayofweek': 5,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol0': {
                                'subv_cost': 41833.29925,
                                'subv_cost_wo_surge': 81329.82742801876,
                                'orders_cnt': 1851.9013750000001,
                                'unique_drivers': 1.057625,
                            },
                            '5fb38a175e48dae578953b08_pol1': {
                                'subv_cost': 19606.781062500002,
                                'subv_cost_wo_surge': 60678.0615,
                                'orders_cnt': 939.6998125,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '00:00',
                            'end_dayofweek': 6,
                            'end_time': '01:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol0': {
                                'subv_cost': 29787.4793125,
                                'subv_cost_wo_surge': 71762.30468519352,
                                'orders_cnt': 1176.0790000000002,
                                'unique_drivers': 1.057625,
                            },
                            '5fb38a175e48dae578953b08_pol1': {
                                'subv_cost': 11167.9911875,
                                'subv_cost_wo_surge': 24813.997750000002,
                                'orders_cnt': 561.598875,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '02:00',
                            'end_dayofweek': 6,
                            'end_time': '03:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol0': {
                                'subv_cost': 43974.4610625,
                                'subv_cost_wo_surge': 84149.10500312621,
                                'orders_cnt': 2191.3990000000003,
                                'unique_drivers': 1.057625,
                            },
                            '5fb38a175e48dae578953b08_pol1': {
                                'subv_cost': 23140.3061875,
                                'subv_cost_wo_surge': 60019.25727272728,
                                'orders_cnt': 1187.7128750000002,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '23:00',
                            'end_dayofweek': 6,
                            'end_time': '00:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol3': {
                                'subv_cost': 103218.38306250001,
                                'subv_cost_wo_surge': 204840.85743619467,
                                'orders_cnt': 2879.3840625000003,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 0,
                            'start_time': '07:00',
                            'end_dayofweek': 0,
                            'end_time': '08:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol3': {
                                'subv_cost': 46157.92787500001,
                                'subv_cost_wo_surge': 75963.02281484634,
                                'orders_cnt': 2258.5581875,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 6,
                            'start_time': '09:00',
                            'end_dayofweek': 6,
                            'end_time': '10:00',
                        },
                    },
                    {
                        'stats': {
                            '5fb38a175e48dae578953b08_pol3': {
                                'subv_cost': 63300.442687500006,
                                'subv_cost_wo_surge': 100935.1376632122,
                                'orders_cnt': 2941.7839375000003,
                                'unique_drivers': 1.057625,
                            },
                        },
                        'interval': {
                            'start_dayofweek': 5,
                            'start_time': '10:00',
                            'end_dayofweek': 5,
                            'end_time': '11:00',
                        },
                    },
                ],
                'budget_summary': {
                    '3': 37516.074,
                    '6': 194953.07387500003,
                    '7': 148553.4786875,
                    '1': 103218.38306250001,
                },
                'warnings': {},
                'restrictions': {},
            },
        ),
        pytest.param(
            '5f9b08b19da21d53ed964474',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': (
                    'result for task 5f9b08b19da21d53ed964474 not found'
                ),
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.config(
    ATLAS_GEOSUBVENTION_RESTRICTIONS={
        '__default__': DEFAULT_RESTRICTIONS_CONF,
    },
)
async def test_v1_geosubventions_tasks_task_id_result_get(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
        mock_taxi_agglomerations,
        mock_tags,
):
    @mock_taxi_agglomerations('/v1/br-geo-nodes/')
    def _mock_parents(request):
        return web.json_response(
            {
                'items': [
                    {
                        'created_at': '2019-01-01T12:12:12',
                        'hierarchy_type': 'BR',
                        'name': 'br_russia',
                        'name_ru': 'Россия',
                        'node_type': 'country',
                    },
                ],
            },
        )

    @mock_taxi_agglomerations('/v1/geo_nodes/get_info/')
    def _mock_node_info(request):
        return web.json_response(
            {
                'items': [
                    {
                        'created_at': '2019-01-01T12:12:12',
                        'hierarchy_type': 'BR',
                        'name': 'br_russia',
                        'name_ru': 'Россия',
                        'node_type': 'country',
                    },
                ],
            },
        )

    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{operation_id}/result/',
    )
    assert response.status == expected_status, await response.text()
    if expected_status == http.HTTPStatus.OK:
        expected_content['restrictions'] = DEFAULT_RESTRICTIONS
        expected_content['warnings'] = DEFAULT_WARNINGS
    assert await response.json() == expected_content


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_warnings',
    (
        pytest.param(
            '7f9b08b19da21d53ed964475',
            http.HTTPStatus.OK,
            {
                'draft_rules': [],
                'general': [],
                'polygons': [],
                'rush_hours': [],
            },
        ),
        pytest.param(
            '7f9b08b19da21d53ed964476',
            http.HTTPStatus.OK,
            {
                'draft_rules': [],
                'general': [
                    {
                        'critical': True,
                        'message': 'Tag bad_tag is not from subventions topic',
                        'type': 'invalid_tag',
                    },
                ],
                'polygons': [],
                'rush_hours': [],
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.config(
    ATLAS_GEOSUBVENTION_RESTRICTIONS={
        '__default__': DEFAULT_RESTRICTIONS_CONF,
    },
)
async def test_v1_geosubventions_tasks_task_id_result_get_check_tags(
        web_app_client,
        operation_id,
        expected_status,
        expected_warnings,
        caplog,
        mock_taxi_agglomerations,
        mock_tags,
):
    @mock_taxi_agglomerations('/v1/br-geo-nodes/')
    def _mock_parents(request):
        return web.json_response(
            {
                'items': [
                    {
                        'created_at': '2019-01-01T12:12:12',
                        'hierarchy_type': 'BR',
                        'name': 'br_russia',
                        'name_ru': 'Россия',
                        'node_type': 'country',
                    },
                ],
            },
        )

    @mock_taxi_agglomerations('/v1/geo_nodes/get_info/')
    def _mock_node_info(request):
        return web.json_response(
            {
                'items': [
                    {
                        'created_at': '2019-01-01T12:12:12',
                        'hierarchy_type': 'BR',
                        'name': 'br_russia',
                        'name_ru': 'Россия',
                        'node_type': 'country',
                    },
                ],
            },
        )

    @mock_tags('/v1/topics/items')
    def _mock_topics_items(request):
        return web.json_response(
            {
                'items': [
                    {
                        'tag': 'super_tag',
                        'topic': 'subventions',
                        'is_financial': True,
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
        )

    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{operation_id}/result/',
    )
    assert response.status == expected_status, await response.text()
    assert (await response.json())['warnings'] == expected_warnings
