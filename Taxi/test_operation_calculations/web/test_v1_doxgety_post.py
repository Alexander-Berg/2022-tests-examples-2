import http

from aiohttp import web
import pytest


class YtSearchMock:
    def __init__(self, attrs_dict, path):
        self.attributes = attrs_dict
        self.path = path

    def __str__(self) -> str:
        return self.path


PARAMS = {
    'cities_config': [{'tariff_zones': ['moscow', 'himki'], 'proportion': 50}],
    'start_date': '2022-03-08',
    'end_date': '2022-03-09',
}
PARAMS_BAD_AGGLOMERATION = {
    'cities_config': [
        {'tariff_zones': ['moscow', 'saratov'], 'proportion': 50},
    ],
    'start_date': '2022-03-08',
    'end_date': '2022-03-09',
}
GEO_NODES = [
    {
        'name': 'br_moscow_near_region',
        'name_ru': 'Ближнее МО',
        'name_en': 'Near MO',
        'node_type': 'node',
        'tariff_zones': ['himki', 'korolev'],
        'parent_name': 'br_moscow',
    },
    {
        'name': 'br_moscow',
        'name_ru': 'Москва',
        'name_en': 'Moscow',
        'node_type': 'agglomeration',
        'tariff_zones': ['moscow'],
        'parent_name': 'br_russia',
    },
    {
        'name': 'br_saratov',
        'name_ru': 'Саратов',
        'name_en': 'Saratov',
        'node_type': 'agglomeration',
        'tariff_zones': ['saratov', 'engels'],
        'parent_name': 'br_russia',
        'region_id': '194',
    },
    {
        'name': 'br_russia',
        'name_ru': 'Россия',
        'name_en': 'Russia',
        'node_type': 'country',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
]


@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
@pytest.mark.parametrize(
    'params, expected_status, expected_response',
    [
        pytest.param(PARAMS, http.HTTPStatus.OK, {'task_id': 'TASK_ID'}),
        pytest.param(
            PARAMS,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'OldTables',
                'details': {'tables': [{'hours_delta': 1, 'path': 'path'}]},
                'message': 'Some of tables contain old data',
            },
            marks=pytest.mark.config(
                OPERATION_CALCULATIONS_DOXGETY_SETTINGS={
                    'algorithms': [
                        {
                            'instance_id': (
                                '5eda9813-f94d-4502-b9d5-6ce111675e9c'
                            ),
                            'name': '__default__',
                            'workflow_id': (
                                'f91b237d-21ad-433f-bc1f-3e0e209ccb44'
                            ),
                        },
                    ],
                    'money_multiplier': 0.8,
                    'targets_complexity': '0.97',
                    'check_tables': [
                        {
                            'root_yt_path': 'path',
                            'diff_day': 1,
                            'node_type': 'table',
                            'suffix': '',
                        },
                    ],
                },
            ),
        ),
        pytest.param(
            PARAMS_BAD_AGGLOMERATION,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ValidationError',
                'message': (
                    'Tariff zones moscow, saratov '
                    'are in different agglomerations'
                ),
            },
        ),
    ],
)
@pytest.mark.now('2020-01-02T01:00:00+00:00')
@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_RESTRICTIONS={
        '__default__': {
            'min_proportion': 20,
            'max_proportion': 80,
            'min_money_multiplier': 0.4,
            'max_money_multiplier': 1.5,
            'min_aa_difficulty': 0.98,
        },
    },
    OPERATION_CALCULATIONS_DOXGETY_SETTINGS={
        'algorithms': [
            {
                'instance_id': 'd5d246e6-9e64-4f10-a561-380ab1d80a17',
                'name': '__default__',
                'workflow_id': 'f91b237d-21ad-433f-bc1f-3e0e209ccb44',
            },
        ],
        'money_multiplier': 0.8,
        'targets_complexity': '0.97',
    },
)
@pytest.mark.geo_nodes(GEO_NODES)
async def test_v1_doxgety_post(
        web_app_client,
        mockserver,
        patch,
        params,
        expected_status,
        expected_response,
        mock_taxi_tariffs,
):
    @patch(
        'operation_calculations.generated.web.yt_wrapper.plugin.'
        'AsyncYTClient.search',
    )
    async def _search(*args, **kwargs):
        return [
            YtSearchMock(
                {'modification_time': '2020-01-01T00:00:00.0Z'}, 'path',
            ),
        ]

    @mockserver.json_handler('/nirvana-api/setGlobalParameters')
    async def _set_params_handler(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/cloneWorkflowInstance')
    async def _clone_handler(request):
        return {'result': 'TASK_ID'}

    @mockserver.json_handler('/nirvana-api/startWorkflow')
    async def _start_handler(request):
        return {'result': 'ok'}

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(
            {
                'zones': [
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'moscow',
                    },
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'himki',
                    },
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'saratov',
                    },
                ],
            },
        )

    response = await web_app_client.post(
        f'/v1/doxgety/', json=params, headers={'X-Yandex-Login': 'test_robot'},
    )
    result = await response.json()
    assert response.status == expected_status
    assert result == expected_response
