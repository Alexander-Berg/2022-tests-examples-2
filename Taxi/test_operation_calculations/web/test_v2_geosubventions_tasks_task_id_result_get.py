import http
import json
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
            '5f9b08b19da21d52ed964473', http.HTTPStatus.OK, 'test_data.json',
        ),
        pytest.param(
            '5f9b08b19da21d52ed964479',
            http.HTTPStatus.OK,
            'test_data_with_warnings.json',
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
async def test_v2_geosubventions_tasks_task_id_result_get(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
        mock_taxi_agglomerations,
        mock_tags,
        open_file,
):
    if isinstance(expected_content, str):
        with open_file(expected_content) as handler:
            expected_content = json.load(handler)

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
        f'/v2/geosubventions/tasks/{operation_id}/result/',
    )
    assert response.status == expected_status, await response.text()
    if expected_status == http.HTTPStatus.OK:
        expected_content['restrictions'] = (
            expected_content['restrictions'] or DEFAULT_RESTRICTIONS
        )
        expected_content['warnings'] = (
            expected_content['warnings'] or DEFAULT_WARNINGS
        )
    assert await response.json() == expected_content
