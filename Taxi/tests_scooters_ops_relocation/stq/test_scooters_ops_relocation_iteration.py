import operator
import os

import pytest

from tests_scooters_ops_relocation import utils


NOW = '2022-01-26T12:00:00+0300'


@pytest.mark.skipif(
    os.getenv('IS_TEAMCITY'),
    reason='I haven\'t been able to install postgis yet',
)
@pytest.mark.parametrize(
    'events',
    [
        pytest.param(
            [
                {
                    'id': 'e1',
                    'type': 'income',
                    'occured_at': (
                        '2022-01-24T12:00:00+0300'
                    ),  # 2 days ago from now
                    'location': (37.538497, 55.907974),  # drops in msk3
                    'extra': {'vehicle_id': 'sc-001-not-on-parking'},
                },
            ],
            id='events in one region',
        ),
        pytest.param(
            [
                {
                    'id': 'e1',
                    'type': 'income',
                    'occured_at': (
                        '2022-01-24T12:00:00+0300'
                    ),  # 2 days ago from now
                    'location': (37.538497, 55.907974),  # drops in msk3
                    'extra': {'vehicle_id': 'sc-001-not-on-parking'},
                },
                {
                    'id': 'e2',
                    'type': 'income',
                    'occured_at': (
                        '2022-01-24T12:00:00+0300'
                    ),  # 2 days ago from now
                    'location': (30.221922, 59.975570),  # drops in spb1
                    'extra': {'vehicle_id': 'sc-spb-001'},
                },
            ],
            id='events in several regions',
        ),
    ],
)
@pytest.mark.config(
    SCOOTERS_REGIONS=[
        {'id': 'moscow', 'name': 'Москва'},
        {'id': 'spb', 'name': 'piter'},
    ],
)
@pytest.mark.experiments3(filename='exp3_polygons.json')
@pytest.mark.experiments3(filename='exp3_settings.json')
@pytest.mark.experiments3(filename='exp3_dynamic_config.json')
@pytest.mark.now(NOW)
async def test(
        pgsql, stq_runner, getuuid, mockserver, load_json, testpoint, events,
):
    for event in events:
        utils.add_event(pgsql, event)

    @testpoint('iteration.polygons_stats')
    def _polygons_stats(request):
        assert request['stats'] == {
            'msk3': {'arrived': 1, 'left': 0},
            'msk1': {'arrived': 0, 'left': 0},
            'msk2': {'arrived': 0, 'left': 0},
            'msk4': {'arrived': 0, 'left': 0},
        }

    @mockserver.json_handler('/scooters-misc/v1/parkings/list')
    def _mock_parkings_list(request):
        return load_json('parkings_list_response.json')

    @testpoint('resource.scooters')
    def _resources_scooters(request):
        assert request == [
            {
                'id': 'sc-001-not-on-parking',
                'status': 'available',
                'location': {'lat': 55.908034, 'lon': 37.538242},
                'polygon_id': 'msk3',
                'parking_place_id': None,
                'stats': {'idle_time': 172800, 'battery_level': 30},
            },
            {
                'id': 'sc-002-on-parking',
                'status': 'available',
                'location': {'lat': 55.908034, 'lon': 37.538242},
                'polygon_id': 'msk3',
                'parking_place_id': 'test_parking_msk_1',
                'parking_place': {
                    'id': 'test_parking_msk_1',
                    'location': {
                        'lat': 55.68304848860712,
                        'lon': 37.341516895783855,
                    },
                },
                'stats': {'idle_time': 604800, 'battery_level': 30},
            },
        ]

    @testpoint('resource.parking_places')
    def _resources_parking_places(request):
        assert request == [
            {
                'id': 'test_parking_msk_1',
                'polygon_id': 'msk3',
                'location': {
                    'lat': 55.68304848860712,
                    'lon': 37.341516895783855,
                },
                'stats': {'capacity': 10, 'scooters_nearby': 1},
            },
        ]

    @testpoint('iteration.pipeline_output')
    def _pipeline_output(request):
        assert request['region'] == 'moscow'
        scooters_to_relocate = sorted(
            request['scooters_to_relocate'],
            key=lambda it: it['scooter']['id'],
        )
        assert scooters_to_relocate == [
            {
                'scooter': {
                    'id': 'sc-001-not-on-parking',
                    'score': 1.0,
                    'location': {'lat': 55.908034, 'lon': 37.538242},
                },
                'computation-info': {'pipeline-name': 'simple'},
            },
            {
                'scooter': {
                    'id': 'sc-002-on-parking',
                    'score': 1.0,
                    'location': {'lat': 55.908034, 'lon': 37.538242},
                    'parking_place': {
                        'id': 'test_parking_msk_1',
                        'location': {
                            'lat': 55.68304848860712,
                            'lon': 37.341516895783855,
                        },
                    },
                },
                'computation-info': {'pipeline-name': 'simple'},
            },
        ]
        assert request['parking_places_to_dropoff'] == [
            {
                'parking_place': {
                    'id': 'test_parking_msk_1',
                    'scooters_to_dropoff': 1,
                    'location': {
                        'lat': 55.68304848860712,
                        'lon': 37.341516895783855,
                    },
                    'stats': {'capacity': 10, 'scooters_nearby': 1},
                    'extra': {
                        'dynamic_config_value': {'aweso': 'me'},
                        'hello': 'me',
                    },
                },
                'computation-info': {'pipeline-name': 'simple'},
            },
        ]

    @mockserver.json_handler(
        '/scooters-ops/scooters-ops/v1/drafts/create-bulk',
    )
    def _mock_drafts_create_bulk(request):
        assert (
            sorted(request.json['drafts'], key=operator.itemgetter('id'))
            == [
                {
                    'id': 'awesome_sc-001-not-on-parking',
                    'expires_at': '2022-01-26T09:10:00+00:00',
                    'typed_extra': {
                        'vehicle_id': 'sc-001-not-on-parking',
                        'score': 1.0,
                        'iteration_id': 'awesome',
                    },
                    'type': 'pickup_vehicle',
                },
                {
                    'id': 'awesome_sc-002-on-parking',
                    'expires_at': '2022-01-26T09:10:00+00:00',
                    'typed_extra': {
                        'vehicle_id': 'sc-002-on-parking',
                        'score': 1.0,
                        'parking_place': {
                            'id': 'test_parking_msk_1',
                            'location': [
                                37.341516895783855,
                                55.68304848860712,
                            ],
                        },
                        'iteration_id': 'awesome',
                    },
                    'type': 'pickup_vehicle',
                },
                {
                    'id': 'awesome_test_parking_msk_1',
                    'expires_at': '2022-01-26T09:10:00+00:00',
                    'typed_extra': {
                        'point_id': 'test_parking_msk_1',
                        'point_type': 'parking_place',
                        'location': [37.341516895783855, 55.68304848860712],
                        'dropoff': 1,
                        'capacity': 10,
                        'occupancy': 1,
                        'score': 1.0,
                        'iteration_id': 'awesome',
                    },
                    'type': 'dropoff_vehicles',
                },
            ]
        )

    await stq_runner.scooters_ops_relocation_iteration.call(
        task_id=getuuid,
        kwargs={'iteration_id': 'awesome', 'region': 'moscow'},
    )

    assert _mock_parkings_list.times_called == 2
    assert _mock_drafts_create_bulk.times_called == 1
    assert _pipeline_output.times_called == 1
    assert _resources_scooters.times_called == 1
    assert _resources_parking_places.times_called == 1
    assert _polygons_stats.times_called == 1

    iteration = utils.get_iterations(pgsql)[0]
    iteration_scooters_to_relocate = sorted(
        iteration.pop('scooters_to_relocate'),
        key=lambda it: it['scooter']['id'],
    )

    assert iteration_scooters_to_relocate == [
        {
            'scooter': {
                'id': 'sc-001-not-on-parking',
                'score': 1.0,
                'location': {'lat': 55.908034, 'lon': 37.538242},
            },
            'computation-info': {'pipeline-name': 'simple'},
        },
        {
            'scooter': {
                'id': 'sc-002-on-parking',
                'score': 1.0,
                'location': {'lat': 55.908034, 'lon': 37.538242},
                'parking_place': {
                    'id': 'test_parking_msk_1',
                    'location': {
                        'lat': 55.68304848860712,
                        'lon': 37.341516895783855,
                    },
                },
            },
            'computation-info': {'pipeline-name': 'simple'},
        },
    ]

    assert iteration == {
        'id': 'awesome',
        'region': 'moscow',
        'created_at': utils.parse_timestring_aware(NOW),
        'parking_places_to_dropoff': [
            {
                'parking_place': {
                    'id': 'test_parking_msk_1',
                    'extra': {
                        'dynamic_config_value': {'aweso': 'me'},
                        'hello': 'me',
                    },
                    'location': {
                        'lat': 55.68304848860712,
                        'lon': 37.341516895783855,
                    },
                    'stats': {'capacity': 10, 'scooters_nearby': 1},
                    'scooters_to_dropoff': 1,
                },
                'computation-info': {'pipeline-name': 'simple'},
            },
        ],
    }


@pytest.mark.skipif(
    os.getenv('IS_TEAMCITY'),
    reason='I haven\'t been able to install postgis yet',
)
@pytest.mark.config(
    SCOOTERS_REGIONS=[
        {'id': 'moscow', 'name': 'Москва'},
        {'id': 'spb', 'name': 'piter'},
    ],
)
@pytest.mark.experiments3(filename='exp3_polygons.json')
@pytest.mark.experiments3(filename='exp3_settings_disabled_drafts.json')
@pytest.mark.experiments3(filename='exp3_dynamic_config.json')
@pytest.mark.now(NOW)
async def test_drafts_create_flag(
        pgsql, stq_runner, getuuid, mockserver, load_json, testpoint,
):
    assert utils.get_iterations(pgsql) == []

    @mockserver.json_handler('/scooters-misc/v1/parkings/list')
    def _mock_parkings_list(request):
        return load_json('parkings_list_response.json')

    await stq_runner.scooters_ops_relocation_iteration.call(
        task_id=getuuid,
        kwargs={'iteration_id': 'awesome', 'region': 'moscow'},
    )

    assert utils.get_iterations(pgsql)[0]['id'] == 'awesome'
