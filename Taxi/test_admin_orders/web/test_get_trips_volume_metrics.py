import aiohttp.web
import pytest


@pytest.mark.config(
    ADMIN_ORDERS_STATISTICS_TRIPS_VOLUME={
        'default_cell_size': 15,
        'available_classes': ['econom'],
        'available_intervals': [15, 30],
        'default_interval': 15,
        'atlas_metric_name': 'trips_volume_detailed_map',
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_content', 'atlas_response'],
    [
        ({'tariff_zones': ['moscow']}, 500, None, None),
        (
            {
                'cell_size': 16,
                'car_class': ['vip'],
                'interval': 15,
                'tariff_zones': ['moscow', 'spb'],
            },
            400,
            {},
            {'data': [], 'meta': {'columns_description': []}},
        ),
        (
            {
                'cell_size': 16,
                'car_class': ['econom'],
                'interval': 17,
                'tariff_zones': ['moscow'],
            },
            400,
            {},
            {'data': [], 'meta': {'columns_description': []}},
        ),
        (
            {
                'cell_size': 16,
                'car_class': ['econom'],
                'interval': 15,
                'tariff_zones': ['moscow', 'spb'],
            },
            200,
            {'data': [{'value': 1, 'quadkey': '1'}]},
            {
                'data': [{'value': 1, 'quadkey': '1'}],
                'meta': {'columns_description': []},
            },
        ),
    ],
)
async def test_get_trips_volume_metrics(
        taxi_admin_orders_web,
        mockserver,
        request_body,
        expected_status,
        expected_content,
        atlas_response,
):
    @mockserver.json_handler('/atlas-backend/v1/data-access/detailed')
    def _mock_get_detailed_info(request):
        if atlas_response is not None:
            return atlas_response
        return aiohttp.web.Response(status=500)

    response = await taxi_admin_orders_web.post(
        '/v1/statistics/trips_volume/', json=request_body,
    )
    assert response.status == expected_status
    if response.status == 200:
        content = await response.json()
        assert content == expected_content
