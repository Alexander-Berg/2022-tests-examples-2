import pytest


@pytest.mark.now('2020-08-18T12:00:00+0300')
@pytest.mark.parametrize(
    'folder,before,timezone',
    [
        ('day', '2020-08-14T00:00:00+03:00', '+03:00'),
        ('week', '2020-08-24T00:00:00+03:00', '+03:00'),
        ('month', '2020-09-01T00:00:00+03:00', '+03:00'),
        ('no_data', '2020-08-14T00:00:00+03:00', '+03:00'),
    ],
)
async def test_v1_driver_money_v1_list_gas_stations(
        taxi_driver_money,
        load_json,
        folder,
        before,
        timezone,
        driver_authorizer,
        fleet_transactions_api,
):
    fleet_transactions_api.set_folder(folder)

    group_by = folder if folder != 'no_data' else 'day'
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before

    response = await taxi_driver_money.get(
        'driver/v1/driver-money/v1/list/gas_stations',
        params=params,
        headers={
            'User-Agent': 'Taximeter 9.20 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '9.20',
            'X-Driver-Session': 'driver_session',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(f'{folder}/service_response.json')
