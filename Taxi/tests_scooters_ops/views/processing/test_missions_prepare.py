import json
import operator

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/processing/missions/prepare'

YAMAPS_OBJECT = {
    'description': 'Москва, Россия',
    'geocoder': {
        'address': {'country': 'Россия', 'formatted_address': ''},
        'id': '8063585',
    },
    'geometry': [37.615928, 55.757333],
    'name': 'Вот в это место надо приехать',
    'uri': 'ymapsbm1://geo?exit1',
}


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'lock_tags': ['lockme']},
    },
)
@pytest.mark.parametrize(
    'expected_tag_add_requests,calls,expected_traits',
    [
        pytest.param(
            [],
            {'mock_car_details': 1},
            ['ReportTagDetails,ReportCars,ReportCarId,ReportStatus'],
            id='just ok',
        ),
        pytest.param(
            [{'object_ids': ['scooter_stub_id_1'], 'tag_name': 'lockme'}],
            {'mock_car_details': 3},
            [
                'ReportTagDetails,ReportCars,ReportCarId,ReportStatus',
                'ReportCars,ReportCarId,ReportStatus',
                'ReportCars,ReportCarId,ReportStatus',
            ],
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
                        'recharge': {
                            'lock_tags': ['lockme'],
                            'lock_on': 'mission_preparing',
                        },
                    },
                ),
            ],
            id='lock drafts here',
        ),
    ],
)
async def test_ok(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        load_json,
        yamaps,
        expected_tag_add_requests,
        calls,
        expected_traits,
):
    db_utils.add_mission(
        pgsql,
        {
            'status': 'preparing',
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )

    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_01',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'scooter_stub_id_1'},
            'mission_id': 'mission_stub_id',
        },
    )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    tag_add_requests = []

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def mock_tag_add(request):
        tag_add_requests.append(request.json)
        assert request.query == {'unique_policy': 'skip_if_exists'}
        return {
            'tagged_objects': [
                {'object_id': 'scooter_stub_id_1', 'tag_id': ['tag_id1']},
            ],
        }

    car_details_traits = []

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert request.args['car_id'] == 'scooter_stub_id_1'
        car_details_traits.append(request.args['traits'])
        return load_json('car_details.json')

    yamaps.add_fmt_geo_object(YAMAPS_OBJECT)

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200
    assert resp.json() == {
        'mission': {
            'id': 'mission_stub_id',
            'status': 'preparing',
            'performer_id': None,
            'comment': '',
            'cargo_claim_id': None,
            'revision': 2,
            'tags': [],
            'created_at': utils.AnyValue(),
            'points': [
                {
                    'id': utils.AnyValue(),
                    'type': 'depot',
                    'status': 'prepared',
                    'revision': 2,
                    'location': [37.0, 55.0],
                    'address': 'Вот в это место надо приехать',
                    'cargo_point_id': None,
                    'order_in_mission': 1,
                    'tags': [],
                    'comment': '',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [
                        {
                            'id': utils.AnyValue(),
                            'type': 'do_nothing',
                            'status': 'prepared',
                            'revision': 3,
                            'order_at_point': 1,
                            'tags': [],
                            'performer_id': None,
                            'comment': '',
                            'created_at': utils.AnyValue(),
                            'updated_at': utils.AnyValue(),
                            'typed_extra': {},
                        },
                    ],
                },
                {
                    'id': utils.AnyValue(),
                    'type': 'scooter',
                    'status': 'prepared',
                    'revision': 2,
                    'location': [37.0, 55.0],
                    'address': 'Вот в это место надо приехать',
                    'cargo_point_id': None,
                    'order_in_mission': 2,
                    'tags': [],
                    'comment': '',
                    'typed_extra': {
                        'scooter': {
                            'id': 'scooter_stub_id_1',
                            'number': '0001',
                        },
                    },
                    'jobs': [
                        {
                            'id': utils.AnyValue(),
                            'type': 'do_nothing',
                            'status': 'prepared',
                            'revision': 3,
                            'order_at_point': 1,
                            'tags': [],
                            'performer_id': None,
                            'comment': '',
                            'created_at': utils.AnyValue(),
                            'updated_at': utils.AnyValue(),
                            'typed_extra': {},
                        },
                    ],
                },
            ],
        },
    }

    assert mock_car_details.times_called == calls.get('mock_car_details', 0)
    assert car_details_traits == expected_traits

    assert mock_tag_add.times_called == len(expected_tag_add_requests)
    assert sorted(
        tag_add_requests, key=operator.itemgetter('tag_name'),
    ) == sorted(expected_tag_add_requests, key=operator.itemgetter('tag_name'))


async def test_not_found(taxi_scooters_ops):
    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 404
    assert resp.json() == {'code': 'not-found', 'message': 'Mission not found'}


async def test_conflict(taxi_scooters_ops, pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'revision': 10,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot_id': 'depot_stub_id'},
                },
                {
                    'type': 'scooter',
                    'typed_extra': {
                        'scooter': {
                            'id': 'scooter_stub_id',
                            'number': 'scooter_stub_number',
                        },
                    },
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 409
    assert resp.json() == {
        'code': 'conflict',
        'message': 'Mission has revision: 10 but 1 requested',
    }


@pytest.mark.parametrize(
    'mission_tags',
    [
        pytest.param(['recharge'], id='mission without car'),
        pytest.param(['recharge', 'vehicle_type_car'], id='mission with car'),
    ],
)
async def test_ok_with_booking(
        taxi_scooters_ops, mockserver, pgsql, load_json, yamaps, mission_tags,
):
    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/depot/accumulator/book',
    )
    async def _accumulator_book(request):
        assert request.json['depot_id'] == 'depot_stub_id'
        assert len(request.json['booking_ids']) == 2
        assert request.json['bookings_must_be_in_one_cabinet'] == (
            mission_tags == ['recharge', 'vehicle_type_car']
        )
        return load_json('depot_accumulator_book_response.json')

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'tags': mission_tags,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [
                        {
                            'type': 'pickup_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_2'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [
                        {
                            'type': 'return_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
            ],
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert sorted(request.args['car_id'].split(',')) == [
            'scooter_stub_id_1',
            'scooter_stub_id_2',
        ]
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        return load_json('car_details.json')

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200
    utils.assert_partial_diff(
        resp.json()['mission']['points'],
        [
            {
                'jobs': [
                    {
                        'revision': 3,
                        'status': 'prepared',
                        'type': 'pickup_batteries',
                        'typed_extra': {
                            'accumulators': [
                                {
                                    'booking_id': utils.AnyValue(),
                                    'cell_id': 'cell_1',
                                    'cabinet_id': 'cab_2',
                                    'cabinet_type': 'charge_station',
                                    'accumulator_id': 'accumulator_1',
                                    'ui_status': 'booked',
                                },
                                {
                                    'booking_id': utils.AnyValue(),
                                    'cell_id': 'cell_1',
                                    'cabinet_id': 'cab_1',
                                    'cabinet_type': 'charge_station',
                                    'accumulator_id': 'accumulator_2',
                                    'ui_status': 'booked',
                                },
                            ],
                        },
                    },
                ],
            },
            {'typed_extra': {'scooter': {'number': '0001'}}},
            {'typed_extra': {'scooter': {'number': '0001'}}},
            {
                'jobs': [
                    {
                        'revision': 3,
                        'status': 'prepared',
                        'type': 'return_batteries',
                        'typed_extra': {'quantity': 2},
                    },
                ],
            },
        ],
    )

    assert _accumulator_book.times_called == 1
    assert mock_car_details.times_called == 1


@pytest.mark.parametrize(
    ['scooter_accumulator_response', 'expected_response'],
    [
        pytest.param(
            {'json': {'code': '409', 'message': 'conflict'}, 'status': 409},
            {'code': 'conflict', 'message': 'booking_ids conflict'},
            id='scooter-accumulator conflict',
        ),
        pytest.param(
            {
                'json': {
                    'code': 'not_enough_accumulators_bookable',
                    'message': 'Not enough',
                },
                'status': 400,
            },
            {
                'code': 'not_enough_accumulators_bookable',
                'message': 'Not enough',
            },
            id='scooter-accumulator not enough accumulators',
        ),
    ],
)
async def test_booking_failed(
        taxi_scooters_ops,
        mockserver,
        pgsql,
        yamaps,
        load_json,
        scooter_accumulator_response,
        expected_response,
):
    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/depot/accumulator/book',
    )
    async def _accumulator_book(request):
        return mockserver.make_response(
            json.dumps(scooter_accumulator_response['json']),
            status=scooter_accumulator_response['status'],
        )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert sorted(request.args['car_id'].split(',')) == [
            'scooter_stub_id_1',
            'scooter_stub_id_2',
        ]
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        return load_json('car_details.json')

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [
                        {
                            'type': 'pickup_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_2'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [
                        {
                            'type': 'return_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert _accumulator_book.times_called == 1
    assert mock_car_details.times_called == 1
    assert resp.status == 400
    assert resp.json() == expected_response


async def test_already_prepared(taxi_scooters_ops, pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'assigning',
            'revision': 10,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot_id': 'depot_stub_id'},
                    'revision': 5,
                    'status': 'planned',
                    'jobs': [
                        {
                            'type': 'do_nothing',
                            'typed_extra': {},
                            'status': 'prepared',
                            'revision': 5,
                        },
                    ],
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 10},
    )

    assert resp.status == 200
    utils.assert_partial_diff(
        resp.json(),
        {
            'mission': {
                'revision': 10,
                'status': 'assigning',
                'points': [
                    {
                        'revision': 5,
                        'status': 'planned',
                        'jobs': [{'revision': 5, 'status': 'prepared'}],
                    },
                ],
            },
        },
    )


@pytest.mark.parametrize(
    'expected_regions',
    [
        pytest.param(
            ['region_1', 'region_2'],
            id='Full config',
            marks=pytest.mark.config(
                SCOOTERS_REGIONS=[
                    {
                        'id': 'region_1',
                        'name': 'Region 1',
                        'area_id': 'area_1',
                    },
                    {
                        'id': 'region_2',
                        'name': 'Region 2',
                        'area_id': 'area_2',
                    },
                ],
            ),
        ),
        pytest.param(
            ['region_1', None],
            id='Partial config',
            marks=pytest.mark.config(
                SCOOTERS_REGIONS=[
                    {
                        'id': 'region_1',
                        'name': 'Region 1',
                        'area_id': 'area_1',
                    },
                ],
            ),
        ),
    ],
)
async def test_region_id(
        taxi_scooters_ops,
        mockserver,
        pgsql,
        load_json,
        expected_regions,
        yamaps,
):
    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        assert request.json['tags'] == ['region_tag']
        areas = {'[12.3, 45.6]': 'area_1', '[78.9, 32.1]': 'area_2'}
        return {
            'areas': [
                {
                    'id': areas[str(request.json['location'])],
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [100.0, 0.0],
                                [101.0, 0.0],
                                [101.0, 1.0],
                                [100.0, 1.0],
                                [100.0, 0.0],
                            ],
                        ],
                    },
                    'tags': [],
                    'revision': '1',
                },
            ],
        }

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'depot',
                    'location': (12.3, 45.6),
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [],
                },
                {
                    'type': 'depot',
                    'location': (78.9, 32.1),
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [],
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200
    regions = [
        point.get('region_id') for point in resp.json()['mission']['points']
    ]
    assert regions == expected_regions

    assert _areas.times_called == 2


async def test_prepare_relocation_jobs(
        taxi_scooters_ops, mockserver, pgsql, load_json, yamaps,
):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'performer_id': 'created',
            'points': [
                {
                    'type': 'parking_place',
                    'location': (35.2, 42.6),
                    'typed_extra': {'parking_place': {'id': 'pp1'}},
                    'jobs': [
                        {
                            'type': 'pickup_vehicles',
                            'typed_extra': {
                                'vehicles': [
                                    {
                                        'id': 'scooter_stub_id_1',
                                        'status': 'problems',
                                        'problems': ['not_found'],
                                    },
                                ],
                            },
                        },
                    ],
                },
                {
                    'type': 'parking_place',
                    'location': (36.2, 42.6),
                    'typed_extra': {'parking_place': {'id': 'pp2'}},
                    'jobs': [
                        {
                            'type': 'dropoff_vehicles',
                            'typed_extra': {'quantity': 1, 'vehicles': []},
                        },
                    ],
                },
            ],
        },
    )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def mock_areas(request):
        return {'areas': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert request.args['car_id'] == 'scooter_stub_id_1'
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        return load_json('car_details.json')

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 200
    utils.assert_partial_diff(
        resp.json(),
        {
            'mission': {
                'points': [
                    {
                        'status': 'prepared',
                        'jobs': [
                            {
                                'type': 'pickup_vehicles',
                                'status': 'prepared',
                                'typed_extra': {
                                    'vehicles': [
                                        {
                                            'id': 'scooter_stub_id_1',
                                            'number': '0001',
                                            'status': 'problems',
                                            'problems': ['not_found'],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        'status': 'prepared',
                        'jobs': [
                            {
                                'type': 'dropoff_vehicles',
                                'status': 'prepared',
                                'typed_extra': {'quantity': 1, 'vehicles': []},
                            },
                        ],
                    },
                ],
            },
        },
    )

    assert mock_areas.times_called == 2
    assert mock_car_details.times_called == 1


@pytest.mark.parametrize(
    ['point', 'expected_tags'],
    [
        pytest.param(
            {
                'type': 'scooter',
                'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                'jobs': [
                    {
                        'job_id': 'job_id_depot_1',
                        'type': 'battery_exchange',
                        'status': 'performing',
                        'typed_extra': {'vehicle_id': 'scooter_stub_id_1'},
                    },
                ],
            },
            ['recharge'],
            id='recharge_mission',
        ),
        pytest.param(
            {
                'type': 'parking_place',
                'typed_extra': {'parking_place': {'id': 'parking_1'}},
                'jobs': [
                    {
                        'job_id': 'pickup_job_1',
                        'type': 'pickup_vehicles',
                        'status': 'performing',
                        'typed_extra': {
                            'vehicles': [
                                {
                                    'id': 'scooter_stub_id_1',
                                    'number': '1337',
                                    'status': 'pending',
                                },
                            ],
                        },
                    },
                ],
            },
            ['relocate', 'new_pro'],
            id='relocate_mission',
        ),
    ],
)
async def test_creating_tags(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        load_json,
        yamaps,
        point,
        expected_tags,
):
    db_utils.add_mission(
        pgsql,
        {
            'status': 'preparing',
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [point],
        },
    )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def _mock_car_details(request):
        assert request.args['car_id'] == 'scooter_stub_id_1'
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        return load_json('car_details.json')

    yamaps.add_fmt_geo_object(YAMAPS_OBJECT)

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200
    assert resp.json()['mission']['tags'] == expected_tags

    assert _mock_car_details.times_called == 1


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {
            'required_tags': ['battery_low'],
            'unlock_tags': ['battery_low'],
        },
    },
)
async def test_bad_draft(taxi_scooters_ops, pgsql, mockserver, yamaps):
    db_utils.add_mission(
        pgsql,
        {
            'status': 'preparing',
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )

    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_01',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'scooter_stub_id_1'},
            'mission_id': 'mission_stub_id',
        },
    )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert request.args['car_id'] == 'scooter_stub_id_1'
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        return {
            'cars': [
                {
                    'id': 'scooter_stub_id_1',
                    'location': {'lat': 55.749735, 'lon': 37.53622833},
                    'model_id': 'ninebot',
                    'number': '0001',
                    'tags': [],
                },
            ],
            'timestamp': 0,
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['scooter_stub_id_1'],
            'tag_names': ['battery_low'],
        }
        return {}

    yamaps.add_fmt_geo_object(YAMAPS_OBJECT)

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 400
    assert resp.json()['code'] == 'bad-draft'

    assert mock_tag_remove.times_called == 1
    assert mock_car_details.times_called == 1

    assert db_utils.get_draft(pgsql, 'draft_01', fields=['status']) == {
        'status': 'failed',
    }


@pytest.mark.config(SCOOTERS_OPS_CAR_IDS_CHUNK_SIZE=1)
async def test_car_details_chunks(
        taxi_scooters_ops, pgsql, mockserver, yamaps, load_json,
):
    db_utils.add_mission(
        pgsql,
        {
            'status': 'preparing',
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_2'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )

    car_id_requests = []

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert (
            request.args['traits']
            == 'ReportTagDetails,ReportCars,ReportCarId,ReportStatus'
        )
        car_id_requests.append(request.args['car_id'])
        return load_json('car_details.json')

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200

    assert mock_car_details.times_called == 2
    assert sorted(car_id_requests) == [
        'scooter_stub_id_1',
        'scooter_stub_id_2',
    ]
