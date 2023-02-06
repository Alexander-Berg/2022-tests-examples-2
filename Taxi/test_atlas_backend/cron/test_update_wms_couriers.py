from aiohttp import web
import pytest

from atlas_backend.generated.cron import run_cron


@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas': {
            '/api/v2/foodtech/couriers': {
                'run_modes': {'atlas_clickhouse': False},
                'run_permission': True,
            },
        },
    },
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {'etl.update_wms_couriers': {'run_permission': True}},
    },
)
@pytest.mark.now('2022-03-31T12:00:00Z')
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['wms_couriers.sql'],
)
async def test_update_wms_couriers(
        atlas_blackbox_mock,
        web_app_client,
        patch,
        response_mock,
        mock_positions,
        mock_grocery_wms,
):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers(*args, **kwargs):
        return {}

    @mock_grocery_wms('/api/external/courier_shifts_v2/updates')
    async def _updates(request):
        return web.json_response(
            {
                'cursor': None,
                'shifts': [
                    {
                        'store_id': (
                            '1163750957874358982942ba851f48ed000300020001'
                        ),
                        'store_external_id': '475723',
                        'courier_id': (
                            '0253f79a86d14b7ab9ac1d5d3017be47_'
                            '1bbad17571444cd57fe36a731223c084'
                        ),
                        'shift_id': (
                            '5169ed17ceb5459abe45f8b8a34ee0c5000400020001'
                        ),
                        'updated_ts': '2022-04-01T13:03:06+00:00',
                        'zone_group_id': (
                            '1163750957874358982942ba851f48ed000300020001'
                        ),
                        'started_at': '2022-04-01T08:00:01+00:00',
                        'closes_at': '2022-04-01T20:03:05+00:00',
                        'status': 'in_progress',
                    },
                    {
                        'store_id': (
                            'c4debd9af8ff4284a7585ae69ed744b6000200020001'
                        ),
                        'store_external_id': '475849',
                        'courier_id': (
                            '0253f79a86d14b7ab9ac1d5d3017be47_'
                            'dd5a025607000a3bc6aceed07993f82e'
                        ),
                        'shift_id': (
                            '3846c002b06141a5b4d7c22bc5e6e12b000200020001'
                        ),
                        'updated_ts': '2022-03-31T17:00:07+00:00',
                        'zone_group_id': (
                            'c4debd9af8ff4284a7585ae69ed744b6000200020001'
                        ),
                        'started_at': '2022-03-31T09:52:24+00:00',
                        'closes_at': '2022-03-31T11:00:06+00:00',
                        'status': 'closed',
                    },
                ],
            },
        )

    @mock_grocery_wms('/api/external/couriers/v1/list')
    async def _list(request):
        return web.json_response(
            {
                'code': 'OK',
                'cursor': None,
                'couriers': [
                    {
                        'courier_id': (
                            '06a65306224e414aa86915a15d5b143f000400020002'
                        ),
                        'external_id': (
                            '0253f79a86d14b7ab9ac1d5d3017be47_'
                            '1bbad17571444cd57fe36a731223c084'
                        ),
                        'first_name': 'Имя',
                        'middle_name': 'Отчество',
                        'last_name': 'Фамилия',
                        'delivery_type': 'foot',
                        'phone_pd_ids': [
                            {'pd_id': '181f39884f174e3a977904b96995a013'},
                        ],
                    },
                    {
                        'courier_id': (
                            'e1927061b71749348c27fbbf199888ff000500020002'
                        ),
                        'external_id': (
                            '0253f79a86d14b7ab9ac1d5d3017be47_'
                            'dd5a025607000a3bc6aceed07993f82e'
                        ),
                        'first_name': 'FirstName',
                        'middle_name': 'MiddleName',
                        'last_name': 'LastName',
                        'delivery_type': 'foot',
                        'phone_pd_ids': [
                            {'pd_id': '309de20b08eb4f08a9e802be4f39c86a'},
                        ],
                    },
                ],
            },
        )

    @patch('atlas_backend.internal.foodtech.free_couriers.get_couriers_info')
    async def _get_couriers_info(*args, **kwargs):
        return []

    await run_cron.main(
        ['atlas_backend.crontasks.update_wms_couriers', '-t', '0'],
    )

    response = await web_app_client.post(
        '/api/v2/foodtech/couriers',
        json={
            'area': {
                'tl': {'lat': 55.557031, 'lon': 37.713127},
                'br': {'lat': 55.886107, 'lon': 37.725203},
            },
        },
    )
    assert response.status == 200, await response.text()
    actual_result = await response.json()
    expected_result = [
        {
            'courier': {
                'id': '06a65306224e414aa86915a15d5b143f000400020002',
                'name': 'Имя Фамилия',
                'position': {'lat': 55.597703, 'lon': 37.722667},
                'shift_type': 'plan',
                'service': 'lavka',
                'status': 'busy',
                'free_time': 0.0,
            },
        },
    ]
    assert len(actual_result) == len(expected_result)
    for courier in actual_result:
        assert courier in expected_result
