import pytest

ENDPOINT = (
    '/drivematics/signalq-drivematics-api/v1/device/status-history/intervals'
)


@pytest.mark.parametrize('expected_response', [200, 400])
async def test_drivematics_v1_device_status_history_intervals(
        taxi_signalq_drivematics_api, mockserver, expected_response,
):
    @mockserver.json_handler(
        f'/signal-device-api/internal/signal-device-api/v1/device/status-history/intervals',  # noqa: E501 pylint: disable=line-too-long
    )
    def _get_status_history(request):
        if expected_response == 200:
            return {
                'intervals': [
                    {
                        'start_at': '2022-03-13T00:00:00+00:00',
                        'end_at': '2022-03-14T00:00:00+00:00',
                        'status': 'turned_on',
                    },
                    {
                        'start_at': '2022-03-12T00:00:00+00:00',
                        'end_at': '2022-03-13T00:00:00+00:00',
                        'status': 'turned_off',
                    },
                ],
            }
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'shit happens'},
        )

    response = await taxi_signalq_drivematics_api.post(
        ENDPOINT,
        json={
            'serial_number': 'SN1',
            'period': {
                'from': '2022-03-12T00:00:00+00:00',
                'to': '2022-03-14T00:00:00+00:00',
            },
            'statuses_intervals_limit': 5,
        },
    )

    assert response.status_code == expected_response, response.text
    if expected_response == 200:
        assert response.json() == {
            'intervals': [
                {
                    'start_at': 1647129600,
                    'end_at': 1647216000,
                    'status': 'turned_on',
                },
                {
                    'start_at': 1647043200,
                    'end_at': 1647129600,
                    'status': 'turned_off',
                },
            ],
        }
