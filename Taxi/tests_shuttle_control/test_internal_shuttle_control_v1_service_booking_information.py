# pylint: disable=import-only-modules, import-error, redefined-outer-name
import datetime

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary


MOCK_NOW_DT = datetime.datetime(2022, 4, 15, 14, 15, 16)


class AnyString:
    def __eq__(self, other):
        return isinstance(other, str)


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


@pytest.fixture
def external_mocks(mockserver, driver_trackstory_v2_shorttracks):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert len(request.json['id_in_set']) == 1
        dbid_uuid = request.json['id_in_set'][0]
        return {
            'profiles': [
                {
                    'park_driver_profile_id': dbid_uuid,
                    'data': {
                        'car_id': 'shuttle_car_id',
                        'full_name': {
                            'first_name': 'ivan',
                            'middle_name': 'i.',
                            'last_name': 'ivanovich',
                        },
                    },
                },
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(100, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'dbid_0_shuttle_car_id',
                    'data': {
                        'number': 'A666MP77',
                        'park_id': 'park_id',
                        'car_id': 'car_id',
                        'color': 'black',
                        'model': 'a1',
                        'brand': 'audi',
                    },
                },
            ],
        }

    def _mock_driver_trackstory():
        return {
            'results': [
                {
                    'position': {
                        'lon': 29.0,
                        'lat': 60.0,
                        'timestamp': 1650032116,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_0',
                },
                {
                    'position': {
                        'lon': 30.0,
                        'lat': 60.0,
                        'timestamp': 1650032116,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_driver_trackstory(),
    )


_RESPONSES = [
    {
        'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        'status': {'status': 'driving'},
        'shuttle': {
            'shuttle_id': 'gkZxnYQ73QGqrKyz',
            'vehicle_info': {
                'car_number': 'A666MP77',
                'color': 'black',
                'model': 'a1',
            },
            'driver_info': {
                'park_id': 'dbid_0',
                'driver_profile_id': 'uuid_0',
                'first_name': 'ivan',
                'last_name': 'ivanovich',
            },
            'position': [29.0, 60.0],
            'is_at_stop': False,
        },
        'route': {
            'route_id': 'gkZxnYQ73QGqrKyz',
            'pickup_stop': {
                'stop_id': 'stop__123',
                'position': [30.002, 60.002],
            },
            'dropoff_stop': {
                'stop_id': 'stop__5',
                'position': [30.008, 60.008],
            },
        },
        'pickup_eta': {
            'time_seconds': 100,
            'distance_meters': 10500,
            'timestamp': (
                MOCK_NOW_DT + datetime.timedelta(seconds=100)
            ).isoformat() + '+0000',
        },
    },
    {
        'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
        'status': {'status': 'finished'},
        'shuttle': {
            'shuttle_id': 'Pmp80rQ23L4wZYxd',
            'vehicle_info': {
                'car_number': 'A666MP77',
                'color': 'black',
                'model': 'a1',
                'vfh_id': '1234567890',
            },
            'driver_info': {
                'park_id': 'dbid_0',
                'driver_profile_id': 'uuid_1',
                'first_name': 'ivan',
                'last_name': 'ivanovich',
            },
            'is_at_stop': False,
        },
        'route': {
            'route_id': 'gkZxnYQ73QGqrKyz',
            'pickup_stop': {
                'stop_id': 'stop__123',
                'position': [30.002, 60.002],
            },
            'dropoff_stop': {
                'stop_id': 'stop__5',
                'position': [30.008, 60.008],
            },
        },
        'pickup_eta': {
            'time_seconds': 0,
            'distance_meters': 0,
            'timestamp': '2020-05-18T15:00:00+0000',
        },
        'dropoff_eta': {
            'time_seconds': 0,
            'distance_meters': 0,
            'timestamp': AnyString(),
        },
    },
]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'booking_id, excepted_response',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', _RESPONSES[0]),
        ('acfff773-398f-4913-b9e9-03bf5eda23ac', _RESPONSES[1]),
    ],
)
async def test_main(
        taxi_shuttle_control,
        external_mocks,
        experiments3,
        booking_id,
        excepted_response,
):
    experiments3.add_config(
        name='shuttle_service_booking_information_settings',
        consumers=['shuttle-control/v1_service_booking_information'],
        match={'enabled': True, 'predicate': {'type': 'true', 'init': {}}},
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'calc_eta_using_cache': False},
            },
        ],
    )

    response = await taxi_shuttle_control.get(
        f'/internal/shuttle-control/v1/service/booking/information'
        f'?service_id=service_origin_1&booking_id={booking_id}',
    )

    assert response.status_code == 200
    assert response.json() == excepted_response
