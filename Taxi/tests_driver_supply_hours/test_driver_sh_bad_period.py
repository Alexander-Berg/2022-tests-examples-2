import pytest

DRIVER_SH_URL = '/v1/parks/drivers-profiles/supply/retrieve'


@pytest.mark.now('2020-03-25T01:00:00+00:00')
@pytest.mark.parametrize(
    'supply_request, response_message',
    [
        (
            {
                'period': {
                    'from': '2020-03-25T01:00:00Z',
                    'to': '2020-03-25T00:00:00Z',
                },
                'aggregate_by': 'hours',
            },
            'period.from should be less then period.to',
        ),
    ],
)
async def test_sh_bad_period(
        taxi_driver_supply_hours, supply_request, response_message,
):
    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': supply_request,
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_period',
        'message': response_message,
    }
