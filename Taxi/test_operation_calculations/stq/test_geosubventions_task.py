import json

from aiohttp import web
import pytest

from taxi import discovery
from taxi.stq import async_worker_ng

import operation_calculations.geosubventions.storage as storage_lib
from operation_calculations.stq import geosubventions_calculator


class MockCh:
    def __init__(self, data):
        self._data = data

    async def execute(self, query, with_column_types=False):
        for element in self._data:
            element_queries = element.get('queries') or [element['query']]
            if query in element_queries:
                return element['data']
        raise ValueError(f'Unknown query: {query}')


@pytest.fixture(autouse=True)
def services(
        request,
        mock_taxi_tariffs,
        mock_geoareas,
        mock_billing_subventions_x,
        patch_aiohttp_session,
        response_mock,
        patch,
        open_file,
):
    services_responses_file = request.node.get_closest_marker(
        'services_responses',
        pytest.mark.services_responses('services_responses.json'),
    ).args[0]

    with open_file(services_responses_file) as file_handler:
        services_responses = json.load(file_handler)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(services_responses['bulk_retrieve'])

    @mock_taxi_tariffs('/v1/tariffs')
    def _get_tariffs(request):
        return web.json_response(services_responses['tariffs'])

    @mock_taxi_tariffs('/v1/tariff_zones')
    def _tariff_zones_handler(request):
        return web.json_response(services_responses['tariff_zones'])

    @mock_geoareas('/geoareas/v1/tariff-areas')
    def _get_tariff_areas(request):
        return web.json_response(services_responses['tariff_areas'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        return web.json_response(services_responses['rules'])

    @patch_aiohttp_session(
        discovery.find_service('chatterbox').url + '/v1/rules/select', 'POST',
    )
    def _patch_request(method, url, **kwargs):
        return response_mock(json=services_responses['rules_old'])

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        assert request.method == 'POST'
        return web.json_response(services_responses['subv_geoareas'])

    @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
    def _patch_getter(item):
        ch_data_file = request.node.get_closest_marker(
            'ch_data', pytest.mark.ch_data('ch_data.json'),
        ).args[0]
        with open_file(ch_data_file) as fin:
            data = json.load(fin)
        return MockCh(data)


@pytest.mark.parametrize(
    'task_id,expected_status,expected_message,expected_errors,new_retry_cnt',
    (
        pytest.param('5f9b08b19da21d53ed964473', 'COMPLETED', None, None, 2),
        pytest.param('5f9b08b19da21d53ed964474', 'COMPLETED', None, None, 1),
        pytest.param(
            '5f9b08b19da21d53ed964491',
            'FAILED',
            'MissingTariffZonesError',
            {
                'test_pol0': {
                    'code': 'MissingTariffZonesError',
                    'missing_zones': 'boryasvo, vko',
                },
            },
            1,
        ),
        pytest.param(
            '5f9b08b19da21d53ed964492',
            'FAILED',
            'GeometryValidationError',
            {
                'invalid_pol0': {
                    'code': 'GeometryValidationError:InvalidGeometry',
                },
                'invalid_pol1': {
                    'code': 'GeometryValidationError:NotClosedPolygon',
                },
                'invalid_pol2': {
                    'code': 'GeometryValidationError:TooManyPoints',
                },
                'invalid_pol3': {
                    'code': 'GeometryValidationError:PolygonWithSpikes',
                },
            },
            1,
        ),
        pytest.param(
            '5f9b08b19da21d53ed964473',
            'FAILED',
            'Task 5f9b08b19da21d53ed964473 exceeded retry limit.'
            ' Current 1 allowed 1',
            None,
            1,
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTIONS={'max_stq_retries': 1},
            ),
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_task(
        stq3_context,
        task_id,
        expected_status,
        expected_message,
        expected_errors,
        new_retry_cnt,
):
    await geosubventions_calculator.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    storage = storage_lib.GeoSubventionsStorage(stq3_context)
    status = await storage.get_task_status(task_id)
    assert status['status'] == expected_status
    if expected_message:
        assert expected_message in status['message']
    if expected_errors:
        assert expected_errors == status['errors']

    new_rez = await storage.get_task_retries(task_id)
    assert new_rez['retry_cnt'] == new_retry_cnt


@pytest.mark.parametrize(
    'task_id, expected_status, expected_message, new_retry_cnt',
    [pytest.param('5f9b08b19da21d53ed964490', 'COMPLETED', None, 1)],
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.services_responses('services_responses_gmv.json')
@pytest.mark.ch_data('ch_data_gmv.json')
async def test_task_gmv(
        task_id,
        expected_status,
        expected_message,
        stq3_context,
        mock_taxi_tariffs,
        new_retry_cnt,
        mock_geoareas,
        mock_billing_subventions_x,
        patch_aiohttp_session,
        response_mock,
        patch,
        open_file,
):
    await geosubventions_calculator.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    with open_file('expected_result.json') as handler:
        expected_result = json.load(handler)
    storage = storage_lib.GeoSubventionsStorage(stq3_context)
    result_gmv = await storage.get_task_result(task_id, as_gmv_summary=True)
    assert result_gmv['budget'] == expected_result['budget']
    assert result_gmv['gmv_summary'] == expected_result['gmv_summary']
    assert result_gmv['draft_rules'] == expected_result['draft_rules']
    assert result_gmv['relevance_summary'] == (
        expected_result['relevance_summary']
    )
