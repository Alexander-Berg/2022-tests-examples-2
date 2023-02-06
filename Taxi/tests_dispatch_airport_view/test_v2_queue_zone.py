import pytest

import tests_dispatch_airport_view.utils as utils

URL = '/driver/v1/dispatch-airport-view/v2/queue_zone'

DRIVER_META = {
    'dbid_uuid0': {'updated_ts': '1000', 'geobus_ts': '1000'},
    'dbid_uuid1': {'updated_ts': '1001', 'geobus_ts': '1001'},
    'dbid_uuid3': {'updated_ts': '1003', 'geobus_ts': '1003'},
    'dbid_uuid4': {'updated_ts': '1004', 'geobus_ts': '1004'},
}


def _make_headers(uuid):
    return {
        **utils.HEADERS,
        'X-YaTaxi-Park-Id': 'dbid',
        'X-YaTaxi-Driver-Profile-Id': uuid,
    }


@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v2_queue_zone(taxi_dispatch_airport_view, load_json):
    etalons = load_json('etalons.json')
    for uuid, etalon in etalons.items():
        actual_response = await taxi_dispatch_airport_view.get(
            URL, params=etalon['request'], headers=_make_headers(uuid),
        )
        assert actual_response.status_code == etalon['response']['status_code']
        if etalon['response']['status_code'] == 200:
            assert actual_response.headers['Cache-Control'] == 'no-cache'
        assert actual_response.json() == etalon['response']['body']
