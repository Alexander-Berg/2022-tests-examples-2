import json


import pytest


ENDPOINT = '/v1/vehicles/branding'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'


def _sorted_csv(items: str):
    return sorted(items.split(', '))


@pytest.mark.parametrize(
    'sticker, lightbox, mock_times_called',
    [(False, True, 1), (True, False, 0)],
)
async def test_vehicles_branding(
        taxi_fleet_vehicles,
        mockserver,
        mongodb,
        sticker,
        lightbox,
        mock_times_called,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body.get('park_id') == 'park1'
        change_info = body.get('change_info')
        assert change_info
        assert change_info.get('object_id') == 'car1'
        assert change_info.get('object_type') == 'MongoDB.Docs.Car.CarDoc'
        diff = change_info.get('diff')
        assert diff and len(diff) == 1
        assert diff[0]['field'] == 'Service'
        assert _sorted_csv(diff[0]['old']) == _sorted_csv(
            'delivery, animals, sticker',
        )
        assert _sorted_csv(diff[0]['new']) == _sorted_csv(
            'delivery, animals, lightbox',
        )
        author = body.get('author')
        assert author == {
            'dispatch_user_id': 'uuid1',
            'display_name': 'driver',
            'user_ip': '',
        }

    old_car = mongodb.dbcars.find_one(
        {'park_id': 'park1', 'car_id': 'car1'},
        {'modified_date', 'updated_ts'},
    )

    response = await taxi_fleet_vehicles.put(
        ENDPOINT,
        params={'park_id': 'park1', 'vehicle_id': 'car1'},
        data=json.dumps(
            {
                'author': {
                    'consumer': 'driver-profile-view',
                    'identity': {
                        'type': 'driver',
                        'driver_profile_id': 'uuid1',
                    },
                },
                'branding': {'sticker': sticker, 'lightbox': lightbox},
            },
        ),
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == mock_times_called

    car = mongodb.dbcars.find_one(
        {'park_id': 'park1', 'car_id': 'car1'},
        {'service', 'modified_date', 'updated_ts'},
    )
    assert car['service']['sticker'] == sticker
    assert car['service']['lightbox'] == lightbox
    assert car['modified_date'] > old_car['modified_date']
    assert car['updated_ts'] > old_car['updated_ts']
