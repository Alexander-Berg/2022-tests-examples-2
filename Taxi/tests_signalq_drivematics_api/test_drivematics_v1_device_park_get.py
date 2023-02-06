ENDPOINT = '/drivematics/signalq-drivematics-api/v1/device/park'


async def test_drivematics_v1_device_get_park(
        taxi_signalq_drivematics_api, mockserver,
):
    @mockserver.json_handler(
        '/signal-device-api/internal/signal-device-api/v1/device/park',  # noqa: E501 pylint: disable=line-too-long
    )
    def _get_park(request):
        return {'park_id': 'nopark'}

    response = await taxi_signalq_drivematics_api.get(
        ENDPOINT, params={'serial_number': 'sn2'},
    )

    assert response.status_code == 200, response.text
    assert response.json()['park_id'] == 'nopark'
