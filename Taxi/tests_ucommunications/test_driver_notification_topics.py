import pytest

UNAUTHORIZED_HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}

AUTHORIZED_HEADERS = {
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'dbid',
    'X-Request-Application': 'uberdriver',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.config(COMMUNICATIONS_DRIVER_TOPICS_POLLING_DELAY=300)
async def test_custom_polling_delay(
        taxi_ucommunications, mock_fleet_parks_list,
):
    response = await taxi_ucommunications.get(
        'driver/v1/ucommunications/notification/topics',
        headers=AUTHORIZED_HEADERS,
        params={'lat': 1, 'lon': 1},
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '300'


@pytest.mark.geoareas(filename='geoareas.json')
async def test_unauthorized_driver(
        taxi_ucommunications, mock_fleet_parks_list,
):
    headers = {
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
    }

    response = await taxi_ucommunications.get(
        'driver/v1/ucommunications/notification/topics',
        headers=headers,
        params={'lat': 55.85, 'lon': 37.55},
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '3600'
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert sorted(response.json()['topics']) == sorted(
        [
            'taximeter:geo:city:Москва:offline',
            'taximeter:geo:city:Московская область:offline',
        ],
    )


@pytest.mark.geoareas(filename='geoareas.json')
async def test_authorized_driver(taxi_ucommunications, mock_fleet_parks_list):
    response = await taxi_ucommunications.get(
        'driver/v1/ucommunications/notification/topics',
        headers=AUTHORIZED_HEADERS,
        params={'lat': 55.85, 'lon': 37.55},
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '3600'
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert set(response.json()['topics']) == {
        'taximeter:park:dbid:online',
        'taximeter:geo:city:Москва:online',
        'taximeter:geo:city:Московская область:online',
        'taximeter:city:Москва:online',
        'taximeter:country:Россия:online',
    }
