import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils

HANDLER = '/scooters-ops/v1/admin/missions/list'
MISSION_1 = {
    'mission_id': 'mission_1',
    'status': 'created',
    'revision': 1,
    'points': [
        {
            'type': 'depot',
            'region_id': 'region_1',
            'typed_extra': {'depot': {'id': 'depot1'}},
        },
        {
            'type': 'scooter',
            'region_id': 'region_2',
            'typed_extra': {'scooter': {'id': 'scooter_id'}},
        },
        {
            'type': 'depot',
            'region_id': 'region_1',
            'typed_extra': {'depot': {'id': 'depot1'}},
        },
    ],
    'created_at': '2000-01-01T12:00:00.00000+00:00',
}
MISSION_2 = {
    'mission_id': 'mission_2',
    'status': 'preparing',
    'revision': 1,
    'points': [],
    'created_at': '2000-01-01T14:00:00.00000+00:00',
}
MISSION_3 = {
    'mission_id': 'mission_3',
    'status': 'performing',
    'revision': 1,
    'points': [],
    'created_at': '2000-01-02T08:00:00.00000+00:00',
}
MISSION_4 = {
    'mission_id': 'mission_4',
    'status': 'completed',
    'revision': 1,
    'points': [
        {
            'type': 'depot',
            'region_id': 'region_1',
            'typed_extra': {'depot': {'id': 'depot2'}},
        },
    ],
    'created_at': '2000-01-03T21:00:00.00000+00:00',
    'tags': ['tag_id1_to_test'],
}
MISSION_5 = {
    'mission_id': 'mission_5',
    'status': 'created',
    'revision': 1,
    'points': [
        {
            'type': 'depot',
            'region_id': 'region_2',
            'typed_extra': {'depot': {'id': 'depot2'}},
            'jobs': [
                {
                    'type': 'pickup_batteries',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'booking_id': 'book_1',
                                'accumulator_id': 'acc_1',
                            },
                        ],
                    },
                },
            ],
        },
    ],
    'created_at': '2022-01-01T12:00:00.00000+00:00',
    'tags': ['tag_id1_to_test', 'tag_id2_to_test'],
}


@pytest.mark.parametrize(
    ['request_body', 'expected_missions_ids'],
    [
        pytest.param(
            {},
            {'mission_1', 'mission_2', 'mission_3', 'mission_4', 'mission_5'},
            id='Without filtration',
        ),
        pytest.param(
            {'statuses': ['preparing', 'completed']},
            {'mission_2', 'mission_4'},
            id='Filter by status',
        ),
        pytest.param(
            {'created': {'after': '2000-01-02T00:00:00.00000+00:00'}},
            {'mission_3', 'mission_4', 'mission_5'},
            id='Created after',
        ),
        pytest.param(
            {'created': {'before': '2000-01-02T00:00:00.00000+00:00'}},
            {'mission_1', 'mission_2'},
            id='Created before',
        ),
        pytest.param(
            {
                'created': {
                    'after': '2000-01-01T13:00:00.00000+00:00',
                    'before': '2000-01-02T12:00:00.00000+00:00',
                },
            },
            {'mission_2', 'mission_3'},
            id='Created range',
        ),
        pytest.param(
            {
                'created': {
                    'after': '2000-01-01T13:00:00.00000+00:00',
                    'before': '2000-01-02T12:00:00.00000+00:00',
                },
                'statuses': ['performing'],
            },
            {'mission_3'},
            id='Created range + filter by statuses',
        ),
        pytest.param(
            {'accumulator_id': 'acc_1'}, {'mission_5'}, id='By accumulator_id',
        ),
        pytest.param(
            {'region_ids': ['region_1']},
            {'mission_1', 'mission_4'},
            id='By one region',
        ),
        pytest.param(
            {'region_ids': ['region_1', 'region_2']},
            {'mission_1', 'mission_4', 'mission_5'},
            id='By two regions',
        ),
        pytest.param(
            {'depot_id': 'depot2'},
            {'mission_4', 'mission_5'},
            id='By depot_id',
        ),
        pytest.param(
            {'tags': ['tag_id1_to_test']},
            {'mission_4', 'mission_5'},
            id='By one tag',
        ),
        pytest.param(
            {'tags': ['tag_id1_to_test', 'tag_id2_to_test']},
            {'mission_5'},
            id='By many tags',
        ),
        pytest.param(
            {
                'tags': [
                    'tag_id1_to_test',
                    'tag_id2_to_test',
                    'tag_id3_to_test',
                ],
            },
            set(),
            id='By many tags, empty response',
        ),
    ],
)
async def test_filtration(
        taxi_scooters_ops, pgsql, request_body, expected_missions_ids,
):
    db_utils.add_mission(pgsql, MISSION_1)
    db_utils.add_mission(pgsql, MISSION_2)
    db_utils.add_mission(pgsql, MISSION_3)
    db_utils.add_mission(pgsql, MISSION_4)
    db_utils.add_mission(pgsql, MISSION_5)

    response = await taxi_scooters_ops.post(HANDLER, request_body)

    assert response.status == 200
    assert {
        mission['id'] for mission in response.json()['missions']
    } == expected_missions_ids


@pytest.mark.parametrize(
    'request_body',
    [
        pytest.param({'id': 'mission'}, id='By mission id'),
        pytest.param({'performer_id': 'performer_1'}, id='By performer id'),
    ],
)
@pytest.mark.parametrize(
    'point_type, point_typed_extra, is_depot_in_response',
    [
        pytest.param(
            'depot',
            {'depot': {'id': 'depot1'}},
            True,
            id='mission_with_depot',
        ),
        pytest.param(
            'scooter',
            {'scooter': {'id': 'scooter_id'}},
            False,
            id='no_depot_in_mission',
        ),
    ],
)
@pytest.mark.config(
    SCOOTERS_REGIONS=[
        {'id': 'region_1', 'name': 'Region 1'},
        {'id': 'region_2', 'name': 'Region 2'},
        {'id': 'region_3', 'name': 'Region 3'},
    ],
    SCOOTERS_OPS_LINKS={
        'performer_profile': 'link/template?{park_clid}_{performer_uuid}',
    },
)
async def test_response(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        request_body,
        point_type,
        point_typed_extra,
        is_depot_in_response,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        assert request.json['id_in_set'] == ['performer_1']
        assert request.json['projection'] == [
            'data.full_name.first_name',
            'data.full_name.last_name',
            'data.full_name.middle_name',
            'data.park_id',
            'data.uuid',
            'data.phone_pd_ids',
        ]
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'performer_1',
                    'data': {
                        'full_name': {
                            'first_name': '1',
                            'last_name': 'Performer',
                            'middle_name': 'Name',
                        },
                        'park_id': 'park_id',
                        'uuid': 'performer-uuid',
                        'phone_pd_ids': [{'pd_id': 'phone_id'}],
                    },
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        assert request.json['query']['park']['ids'] == ['park_id']
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': '',
                    'name': '',
                    'is_active': True,
                    'city_id': '',
                    'locale': '',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': '',
                    'demo_mode': False,
                    'geodata': {'lon': 12.3, 'lat': 45.6, 'zoom': 11},
                    'provider_config': {'type': 'none', 'clid': 'park-clid'},
                },
            ],
        }

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission',
            'status': 'performing',
            'performer_id': 'performer_1',
            'points': [
                {
                    'type': point_type,
                    'typed_extra': point_typed_extra,
                    'region_id': 'region_1',
                    'status': 'visited',
                    'address': 'Вот этот адрес',
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_id'}},
                    'region_id': 'region_2',
                    'status': 'visited',
                    'jobs': [
                        {
                            'type': 'battery_exchange',
                            'typed_extra': {'vehicle_id': 'vehicle_1'},
                        },
                    ],
                },
                {
                    'type': point_type,
                    'typed_extra': point_typed_extra,
                    'region_id': 'region_1',
                    'address': 'Не этот адрес',
                },
            ],
            'tags': ['tag_id1_to_test', 'tag_id2_to_test', 'tag_id3_to_test'],
        },
    )

    response = await taxi_scooters_ops.post(HANDLER, request_body)
    assert response.status == 200

    expected_response = [
        {
            'created_at': utils.AnyValue(),
            'id': 'mission',
            'points_status': {'count': 3, 'left': 1},
            'performer': {
                'name': 'Performer 1 Name',
                'phone_pd_id': 'phone_id',
                'link': 'link/template?park-clid_performer-uuid',
            },
            'regions': [
                {'id': 'region_1', 'name': 'Region 1'},
                {'id': 'region_2', 'name': 'Region 2'},
            ],
            'status': 'performing',
            'tags': ['tag_id1_to_test', 'tag_id2_to_test', 'tag_id3_to_test'],
        },
    ]

    if is_depot_in_response:
        expected_response[0]['depot'] = {'address': 'Вот этот адрес'}

    assert response.json()['missions'] == expected_response


async def test_cursor(taxi_scooters_ops, pgsql):
    def get_mission_ids(response):
        return {mission['id'] for mission in response.json()['missions']}

    db_utils.add_mission(pgsql, MISSION_1)
    db_utils.add_mission(pgsql, MISSION_2)
    db_utils.add_mission(pgsql, MISSION_3)
    db_utils.add_mission(pgsql, MISSION_4)
    db_utils.add_mission(pgsql, MISSION_5)

    response1 = await taxi_scooters_ops.post(HANDLER, {}, params={'limit': 2})
    assert response1.status == 200
    assert get_mission_ids(response1) == {'mission_4', 'mission_5'}

    cursor1 = response1.json()['cursor']
    response2 = await taxi_scooters_ops.post(
        HANDLER, {}, params={'limit': 2, 'cursor': cursor1},
    )
    assert response2.status == 200
    assert get_mission_ids(response2) == {'mission_2', 'mission_3'}

    cursor2 = response2.json()['cursor']
    response3 = await taxi_scooters_ops.post(
        HANDLER, {}, params={'limit': 2, 'cursor': cursor2},
    )
    assert response3.status == 200
    assert response3.json().get('cursor') is None
    assert get_mission_ids(response3) == {'mission_1'}


async def test_ordering(taxi_scooters_ops, pgsql):
    db_utils.add_mission(pgsql, MISSION_1)
    db_utils.add_mission(pgsql, MISSION_2)
    db_utils.add_mission(pgsql, MISSION_3)
    db_utils.add_mission(pgsql, MISSION_4)
    db_utils.add_mission(pgsql, MISSION_5)

    response = await taxi_scooters_ops.post(HANDLER, {})

    assert response.status == 200
    assert [mission['id'] for mission in response.json()['missions']] == [
        'mission_5',
        'mission_4',
        'mission_3',
        'mission_2',
        'mission_1',
    ]
