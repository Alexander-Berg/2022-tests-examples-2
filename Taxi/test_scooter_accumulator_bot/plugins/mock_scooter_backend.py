import aiohttp.web
import pytest


def scooter_backend_car_details(request):
    assert request.method == 'GET'

    if request.query['car_number'] != '100':
        return (
            200,
            {
                'timestamp': 1648646528,
                'cars': [
                    {
                        'number': request.query['car_number'],
                        'model_id': 'ninebot',
                        'id': '0d00b5b3-93fd-49f0-91a4-12f7eaec46e7',
                        'location': {'lat': 45.034436, 'lon': 38.973891},
                        'lag': {
                            'heartbeat': 1645196300,
                            'host': 'host:port',
                            'created': 1645112056,
                            'location': 1648643892,
                            'blackbox': 1644148882,
                        },
                        'telematics': {
                            'fuel_level': 99,
                            'fuel_distance': 75.480768,
                            'remaining_time': 18000,
                        },
                    },
                ],
            },
        )
    return 404, {}


def scooter_backend_car_telematics(request):
    assert request.method == 'GET'

    if request.query['car_id'] == '0d00b5b3-93fd-49f0-91a4-12f7eaec46e7':
        return (
            200,
            {
                'sensors': [
                    {
                        'id': 2,
                        'name': 'mcu_firmware',
                        'since': 1649925618,
                        'updated': 1650372888,
                        'value': None,
                    },
                    {
                        'id': 2,
                        'name': 'mcu_firmware_revision',
                        'since': 1649925618,
                        'subid': 1,
                        'updated': 1650372888,
                        'value': 0,
                    },
                    {
                        'id': 3,
                        'name': 'gsm_firmware',
                        'since': 1650372888,
                        'updated': 1650372888,
                        'value': '0512',
                    },
                    {
                        'id': 4,
                        'name': 'gps_firmware',
                        'since': 1650040047,
                        'updated': 1650372888,
                        'value': 'LC29DCNR01A02S_2WDR_HYF',
                    },
                    {
                        'id': 33002,
                        'name': 'ble_firmware_version',
                        'since': 1650364088,
                        'updated': 1650372888,
                        'value': 242,
                    },
                ],
            },
        )
    return 404, {}


@pytest.fixture
def scooter_accumulator_bot_scooter_backend_mocks(
        mock_scooter_backend,
):  # pylint: disable=C0103
    @mock_scooter_backend('/api/taxi/car/details')
    async def _car_details(request):
        code, json = scooter_backend_car_details(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_scooter_backend('/api/taxi/car/telematics/state')
    async def _car_telematics(request):
        code, json = scooter_backend_car_telematics(request)
        return aiohttp.web.json_response(json, status=code)
