import pytest


DEFAULT_HEADERS = {
    'X-YaTaxi-Driver-Profile-Id': 'driver',
    'X-YaTaxi-Park-Id': 'MskPark',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}


async def test_remove_feeds(taxi_driver_wall, mockserver):
    @mockserver.json_handler('/feeds/v1/batch/remove')
    def _mock_feeds(request):
        request_json = request.json

        for i in request_json['items']:
            channels = i.pop('channels')
            assert set(channels) == set(
                [
                    'uberdriver:Driver:MskPark:driver',
                    'vezet:Driver:MskPark:driver',
                    'taximeter:Driver:MskPark:driver',
                ],
            )
        assert request_json == {
            'items': [
                {
                    'service': 'driver-wall',
                    'feed_id': '555b56eec1794602ac85a7e3ba53450e',
                },
                {
                    'service': 'driver-fullscreen',
                    'feed_id': '555b56eec1794602ac85a7e3ba53450e',
                },
            ],
        }
        return {'statuses': {'555b56eec1794602ac85a7e3ba53450e': 200}}

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/remove',
        params={'id': '555b56eec1794602ac85a7e3ba53450e'},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()


async def test_remove_feeds_404(taxi_driver_wall, mockserver):
    @mockserver.json_handler('/feeds/v1/batch/remove')
    def _mock_feeds(request):
        return {'statuses': {'555b56eec1794602ac85a7e3ba53450e': 404}}

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/remove',
        params={'id': '555b56eec1794602ac85a7e3ba53450e'},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.config(
    DRIVER_WALL_FEEDS_SERVICES=[
        'driver-wall',
        'driver-fullscreen',
        'other-service',
    ],
)
async def test_remove_by_request_id(taxi_driver_wall, mockserver):
    @mockserver.json_handler('/feeds/v1/batch/remove_by_request_id')
    def _mock_feeds(request):
        assert request.json == {
            'items': [
                {
                    'recursive': False,
                    'service': 'driver-wall',
                    'request_id': 'my-request-id',
                },
                {
                    'recursive': False,
                    'service': 'driver-fullscreen',
                    'request_id': 'my-request-id',
                },
                {
                    'recursive': False,
                    'service': 'other-service',
                    'request_id': 'my-request-id',
                },
            ],
        }
        return {'statuses': {}}

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/remove',
        json={'request_ids': ['my-request-id']},
    )
    assert response.status_code == 200


@pytest.mark.config(
    DRIVER_WALL_FEEDS_SERVICES=[
        'driver-wall',
        'driver-fullscreen',
        'other-service',
    ],
)
async def test_remove_feeds_services_config(
        taxi_driver_wall, mockserver, load_json,
):
    @mockserver.json_handler('/feeds/v1/batch/remove')
    def _mock_feeds(request):
        request_json = request.json

        for i in request_json['items']:
            channels = i.pop('channels')
            assert set(channels) == set(
                [
                    'uberdriver:Driver:MskPark:driver',
                    'vezet:Driver:MskPark:driver',
                    'taximeter:Driver:MskPark:driver',
                ],
            )

        assert request_json == load_json(
            'feeds_remove_several_services_request.json',
        )
        return {'statuses': {'555b56eec1794602ac85a7e3ba53450e': 200}}

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/remove',
        params={'id': '555b56eec1794602ac85a7e3ba53450e'},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_feeds.times_called == 1
