import json

import pytest


LON = 37.604459
LAT = 55.754762


@pytest.mark.redis_store(['set', 'DriverSession:777:qwerty', '888'])
@pytest.mark.parametrize(
    'zoomlevel,allowed,title,subtitle',
    [
        (1, True, 'Россия', 'Россия'),
        (
            4,
            False,
            'Россия, Центральный федеральный округ',
            'Центральный федеральный округ',
        ),
        (6, True, 'Россия, Москва', 'Москва'),
        (8, False, 'Россия, Москва', 'Центральный административный округ'),
        (
            10,
            True,
            'Россия, Москва, Центральный административный округ',
            'Пресненский район',
        ),
        (16, True, 'Россия, Москва', 'Малый Кисловский переулок, 4с5'),
    ],
)
def test_point_suggest(
        taxi_driver_protocol,
        driver_authorizer_service,
        zoomlevel,
        allowed,
        title,
        subtitle,
        mockserver,
        load_json,
        config,
):
    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        data = json.loads(request.get_data())
        assert data == {
            'check_points': [{'mode': 'home', 'position': [LON, LAT]}],
        }
        return {
            'checked_points': [
                {
                    'position': [LON, LAT],
                    'mode': 'home',
                    'accepted': allowed,
                    'message': (
                        None if allowed else 'you cant setup home point'
                    ),
                },
            ],
        }

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        data = request.args.to_dict()
        assert data['lang'] == 'ru'
        assert data['origin'] == 'mobile-taxi'
        assert data['type'] == 'geo'
        assert data['results'] == '1'
        assert data['skip'] == '0'
        assert data['ll'] == str(LON) + ',' + str(LAT)
        assert data['text'] == str(LON) + ',' + str(LAT)
        assert data['geocoder_pin'] == '1'
        assert data['z'] == str(zoomlevel)
        return load_json('search_zoom_' + str(zoomlevel) + '_response.json')

    url = (
        'driver/reverse_geocoding?db=777&session=qwerty&mode=home&lon='
        + str(LON)
        + '&lat='
        + str(LAT)
        + '&zoomlevel='
        + str(zoomlevel)
    )

    response = taxi_driver_protocol.get(url, headers={'Accept-Language': 'ru'})
    data = {'title': title, 'subtitle': subtitle, 'allowed': allowed}
    if not allowed:
        data['disallowed_reason'] = 'you cant setup home point'

    assert response.status_code == 200
    assert response.json() == data

    assert mock_yamaps.times_called == 1
    assert mock_check_point.times_called == 1


@pytest.mark.redis_store(['set', 'DriverSession:777:qwerty', '888'])
def test_no_point_suggest(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        load_json,
        config,
):
    @mockserver.json_handler(
        '/reposition_api/internal/reposition-api/v1/drivers/check_points',
    )
    def mock_check_point(request):
        data = json.loads(request.get_data())
        assert data == {
            'check_points': [{'mode': 'home', 'position': [LON, LAT]}],
        }
        return {
            'checked_points': [
                {
                    'position': [LON, LAT],
                    'mode': 'home',
                    'accepted': False,
                    'message': 'you cant setup home point',
                },
            ],
        }

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        data = request.args.to_dict()
        assert data['lang'] == 'ru'
        assert data['origin'] == 'mobile-taxi'
        assert data['type'] == 'geo'
        assert data['results'] == '1'
        assert data['skip'] == '0'
        assert data['ll'] == str(LON) + ',' + str(LAT)
        assert data['text'] == str(LON) + ',' + str(LAT)
        assert data['geocoder_pin'] == '1'
        assert data['z'] == '1'
        return load_json('search_no_point_response.json')

    url = (
        'driver/reverse_geocoding?db=777&session=qwerty&mode=home&lon='
        + str(LON)
        + '&lat='
        + str(LAT)
        + '&zoomlevel=1'
    )

    response = taxi_driver_protocol.get(url, headers={'Accept-Language': 'ru'})
    assert response.status_code == 500
    assert mock_yamaps.times_called == 1
