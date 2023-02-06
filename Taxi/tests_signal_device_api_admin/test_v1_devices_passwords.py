import pytest

ENDPOINT = 'v1/devices/passwords'

OK_PARAMS = [
    (
        'e58e753c44e548ce9edaec0e0ef9c8c1',
        {
            'bluetooth_password': 'blue.tooth.password.1',
            'wifi_password': 'wi.fi.pw.1',
            'user_password': 'u.s.e.r.1.to.floor.recognize',
        },
    ),
    (
        '4306de3dfd82406d81ea3c098c80e9ba',
        {
            'bluetooth_password': 'blue.tooth.password.2',
            'wifi_password': 'wi.fi.pw.2',
            'user_password': 'u.s.e.r.2.above.generation.act',
        },
    ),
    (
        '6b3b9123656f4a808ce3e7c52a0be835',
        {
            'bluetooth_password': 'blue.tooth.password.3',
            'wifi_password': 'wi.fi.pw.3',
            'user_password': 'u.s.e.r.3.majority.support.appear',
        },
    ),
    (
        '77748dae0a3244ebb9e1b8d244982c28',
        {
            'bluetooth_password': 'blue.tooth.password.4',
            'wifi_password': 'wi.fi.pw.4',
            'user_password': 'u.s.e.r.4.it.enough.amount',
        },
    ),
]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize('device_id, passwords', OK_PARAMS)
async def test_ok(taxi_signal_device_api_admin, device_id, passwords):
    response = await taxi_signal_device_api_admin.get(
        ENDPOINT, params={'device_id': device_id},
    )

    assert response.status_code == 200, response.text

    response_json = response.json()
    assert response_json.pop('device_id') == device_id
    assert response_json == passwords


async def test_not_found(taxi_signal_device_api_admin):
    response = await taxi_signal_device_api_admin.get(
        ENDPOINT, params={'device_id': 'aaeedd'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': '404',
        'message': 'device with id `aaeedd` is not registered',
    }
