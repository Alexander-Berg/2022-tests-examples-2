import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/park/demo-mode'


@pytest.mark.pgsql('signal_device_api_meta_db', files=['park_mode.sql'])
@pytest.mark.parametrize(
    'park_id, is_in_demo',
    [
        pytest.param('p1', True, id='True in db'),
        pytest.param('p2', False, id='False in db'),
        pytest.param('p3', False, id='False, but not in db yet'),
    ],
)
async def test_regime_get(
        taxi_signal_device_api_admin, mockserver, park_id, is_in_demo,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == 200, response.text

    assert response.json()['is_in_demo_mode'] == is_in_demo


@pytest.mark.pgsql('signal_device_api_meta_db', files=['park_mode.sql'])
@pytest.mark.parametrize(
    'park_id, new_mode, expected_code',
    [
        pytest.param('p1', 'normal', 200, id='Switched from Demo'),
        pytest.param('p1', 'demo', 200, id='Already Demo'),
        pytest.param('p2', 'demo', 200, id='Switched to Demo'),
        pytest.param('p3', 'demo', 200, id='Was not in db'),
        pytest.param('p4', 'normal', 403, id='Not SignalQ'),
    ],
)
async def test_regime_post(
        taxi_signal_device_api_admin,
        mockserver,
        park_id,
        new_mode,
        expected_code,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        specifications = ['taxi']
        if park_id != 'p4':
            specifications = ['signalq']
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': specifications,
                },
            ],
        }

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
        json={'new_mode': new_mode},
    )
    assert response.status_code == expected_code, response.text

    if expected_code == 200:
        assert response.json()['is_in_demo_mode'] == (new_mode == 'demo')
