import json

import bson
import pytest

PERIODIC_NAME = 'periodic-sync-digitalbox'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'


@pytest.mark.parametrize(
    'car_with_digitalbox_ids, car_with_lightbox_ids, '
    'changed_park, old_amenities',
    [
        pytest.param(
            [{'_id': '0001'}],
            [{'_id': '0002'}],
            'park1',
            '',
            id='add_digitalbox_only_number_normalized',
            marks=[
                pytest.mark.config(
                    FLEET_VEHICLES_SYNC_DIGITALBOX_SETTINGS={
                        'parks_not_to_sync': [],
                        'cars_with_digitalbox': ['A111AA'],
                        'interval': 30,
                    },
                ),
            ],
        ),
        pytest.param(
            [{'_id': '0002'}],
            [],
            'park2',
            'lightbox',
            id='add_digitalbox_removing_lightbox_just_number',
            marks=[
                pytest.mark.config(
                    FLEET_VEHICLES_SYNC_DIGITALBOX_SETTINGS={
                        'parks_not_to_sync': [],
                        'cars_with_digitalbox': ['Б222ББ'],
                        'interval': 30,
                    },
                ),
            ],
        ),
        pytest.param(
            [{'_id': bson.ObjectId('5bc089ad66254ff32527ed67')}],
            [{'_id': '0002'}],
            'park3',
            '',
            id='add_digitalbox_not_to_all_parks_number_half_normalized',
            marks=[
                pytest.mark.config(
                    FLEET_VEHICLES_SYNC_DIGITALBOX_SETTINGS={
                        'parks_not_to_sync': ['park4'],
                        'cars_with_digitalbox': ['Г333GГ'],
                        'interval': 30,
                    },
                ),
            ],
        ),
    ],
)
async def test_periodic_sync_digitalbox(
        taxi_fleet_vehicles,
        mongodb,
        car_with_digitalbox_ids,
        car_with_lightbox_ids,
        changed_park,
        old_amenities,
        mockserver,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': changed_park,
            'change_info': {
                'object_id': 'car1',
                'object_type': 'MongoDB.Docs.Car.CarDoc',
                'diff': [
                    {
                        'field': 'Service',
                        'old': old_amenities,
                        'new': 'digital_lightbox',
                    },
                ],
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': PERIODIC_NAME,
                'user_ip': '',
            },
        }
        return mockserver.make_response(status=200)

    await taxi_fleet_vehicles.run_task(PERIODIC_NAME)

    real_car_with_digitalbox_ids = list(
        mongodb.dbcars.find({'service.digital_lightbox': True}, {'_id': True}),
    )

    assert real_car_with_digitalbox_ids == car_with_digitalbox_ids

    real_car_with_lighbox_ids = list(
        mongodb.dbcars.find({'service.lightbox': True}, {'_id': True}),
    )

    assert real_car_with_lighbox_ids == car_with_lightbox_ids

    assert _mock_change_logger.times_called == 1
