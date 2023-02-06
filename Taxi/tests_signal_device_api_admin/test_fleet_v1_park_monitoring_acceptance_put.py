import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/park/monitoring-acceptance'


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.parametrize(
    'park_id, specifications, expected_code',
    [
        ('p1', ['taxi', 'signalq'], 200),
        ('p2', ['taxi', 'signalq'], 200),
        ('p3', ['signalq'], 200),
        ('p4', ['taxi'], 403),
        ('p5', [], 403),
    ],
)
async def test_acceptance_put(
        taxi_signal_device_api_admin,
        mockserver,
        pgsql,
        park_id,
        specifications,
        expected_code,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': park_id,
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'specifications': specifications,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == expected_code, response.text

    if expected_code != 200 or len(specifications) < 2:
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT EXISTS ( '
        '   SELECT TRUE '
        '   FROM signal_device_api.monitoring_acceptance '
        f'   WHERE park_id = \'{park_id}\' '
        ') as does_acceptance_exist ',
    )
    db_result = list(db)
    assert db_result[0][0]
