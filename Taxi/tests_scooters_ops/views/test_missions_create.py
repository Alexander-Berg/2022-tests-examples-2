import copy

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/missions/create'
RECHARGE_2_SCOOTERS_REQUEST = {
    'performer_id': 'performer',
    'related_drafts': [],
    'tags': ['mission_tag_1', 'mission_tag_2'],
    'points': [
        {
            'type': 'depot',
            'location': [35.2, 42.6],
            'tags': ['point_tag_1', 'point_tag_2'],
            'typed_extra': {'depot': {'id': 'depot'}},
            'jobs': [
                {'type': 'pickup_batteries', 'typed_extra': {'quantity': 1}},
            ],
        },
        {
            'type': 'scooter',
            'location': [35.4, 42.1],
            'eta': '2022-04-01T07:00:00+00:00',
            'typed_extra': {'scooter': {'id': 'scooter_id'}},
            'tags': ['point_tag_2', 'point_tag_3'],
            'jobs': [
                {
                    'type': 'battery_exchange',
                    'expected_execution_time_s': 300,
                    'typed_extra': {'vehicle_id': 'scooter_id'},
                    'tags': ['job_tag_1', 'job_tag_1'],
                },
            ],
        },
        {
            'type': 'depot',
            'location': [35.2, 42.6],
            'typed_extra': {'depot': {'id': 'depot'}},
            'jobs': [
                {'type': 'return_batteries', 'typed_extra': {'quantity': 1}},
            ],
        },
    ],
}


@pytest.mark.parametrize(
    'drafts,request_body,expected_mission',
    [
        pytest.param(
            [
                {
                    'draft_id': 'draft_1',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vehicle_1'},
                },
                {
                    'draft_id': 'draft_2',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vehicle_2'},
                },
            ],
            {
                **copy.deepcopy(RECHARGE_2_SCOOTERS_REQUEST),
                **{'related_drafts': ['draft_1', 'draft_2']},
            },
            {
                'id': 'mission_id',
                'status': 'created',
                'performer_id': 'performer',
                'tags': ['mission_tag_1', 'mission_tag_2'],
                'comment': '',
                'revision': 1,
                'created_at': utils.AnyValue(),
                'cargo_claim_id': None,
                'points': [
                    {
                        'id': utils.AnyValue(),
                        'comment': '',
                        'location': [35.2, 42.6],
                        'order_in_mission': 1,
                        'revision': 1,
                        'status': 'created',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot'}},
                        'tags': ['point_tag_1', 'point_tag_2'],
                        'cargo_point_id': None,
                        'jobs': [
                            {
                                'id': utils.AnyValue(),
                                'type': 'pickup_batteries',
                                'status': 'created',
                                'revision': 1,
                                'order_at_point': 1,
                                'performer_id': None,
                                'comment': '',
                                'created_at': utils.AnyValue(),
                                'updated_at': utils.AnyValue(),
                                'typed_extra': {'quantity': 1},
                            },
                        ],
                    },
                    {
                        'id': utils.AnyValue(),
                        'comment': '',
                        'location': [35.4, 42.1],
                        'eta': '2022-04-01T07:00:00+00:00',
                        'order_in_mission': 2,
                        'revision': 1,
                        'status': 'created',
                        'type': 'scooter',
                        'typed_extra': {'scooter': {'id': 'scooter_id'}},
                        'tags': ['point_tag_2', 'point_tag_3'],
                        'cargo_point_id': None,
                        'jobs': [
                            {
                                'id': utils.AnyValue(),
                                'type': 'battery_exchange',
                                'expected_execution_time_s': 300,
                                'status': 'created',
                                'revision': 1,
                                'order_at_point': 1,
                                'performer_id': None,
                                'comment': '',
                                'created_at': utils.AnyValue(),
                                'updated_at': utils.AnyValue(),
                                'typed_extra': {'vehicle_id': 'scooter_id'},
                                'tags': ['job_tag_1'],
                            },
                        ],
                    },
                    {
                        'id': utils.AnyValue(),
                        'comment': '',
                        'location': [35.2, 42.6],
                        'order_in_mission': 3,
                        'revision': 1,
                        'status': 'created',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot'}},
                        'cargo_point_id': None,
                        'jobs': [
                            {
                                'id': utils.AnyValue(),
                                'type': 'return_batteries',
                                'status': 'created',
                                'revision': 1,
                                'order_at_point': 1,
                                'performer_id': None,
                                'comment': '',
                                'created_at': utils.AnyValue(),
                                'updated_at': utils.AnyValue(),
                                'typed_extra': {'quantity': 1},
                            },
                        ],
                    },
                ],
            },
            id='recharge mission',
        ),
        pytest.param(
            [],
            {
                'performer_id': 'performer',
                'tags': ['relocate_mission'],
                'related_drafts': [],
                'points': [
                    {
                        'type': 'parking_place',
                        'location': [35.2, 42.6],
                        'typed_extra': {'parking_place': {'id': 'pp1'}},
                        'jobs': [
                            {
                                'type': 'pickup_vehicles',
                                'typed_extra': {
                                    'vehicles': [{'id': 'vehicle-1'}],
                                },
                            },
                        ],
                    },
                    {
                        'type': 'parking_place',
                        'location': [36.2, 42.6],
                        'typed_extra': {'parking_place': {'id': 'pp2'}},
                        'jobs': [
                            {
                                'type': 'dropoff_vehicles',
                                'typed_extra': {'quantity': 1},
                            },
                        ],
                    },
                ],
            },
            {
                'id': 'mission_id',
                'status': 'created',
                'tags': ['relocate_mission'],
                'points': [
                    {
                        'location': [35.2, 42.6],
                        'status': 'created',
                        'type': 'parking_place',
                        'typed_extra': {'parking_place': {'id': 'pp1'}},
                        'jobs': [
                            {
                                'type': 'pickup_vehicles',
                                'status': 'created',
                                'typed_extra': {
                                    'vehicles': [{'id': 'vehicle-1'}],
                                },
                            },
                        ],
                    },
                    {
                        'location': [36.2, 42.6],
                        'status': 'created',
                        'type': 'parking_place',
                        'typed_extra': {'parking_place': {'id': 'pp2'}},
                        'jobs': [
                            {
                                'type': 'dropoff_vehicles',
                                'status': 'created',
                                'typed_extra': {'quantity': 1},
                            },
                        ],
                    },
                ],
            },
            id='relocation mission',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        drafts,
        request_body,
        expected_mission,
):
    for draft in drafts:
        db_utils.add_draft(pgsql, draft)

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def _mock_processing_create_event(request):
        assert request.headers['X-Idempotency-Token'] == 'created-mission_id'
        assert request.json['kind'] == 'created'
        utils.assert_partial_diff(request.json['mission'], expected_mission)
        return {'event_id': 'idontcare'}

    response = await taxi_scooters_ops.post(
        HANDLER, request_body, params={'mission_id': 'mission_id'},
    )

    assert response.status == 200
    utils.assert_partial_diff(response.json(), {'mission': expected_mission})

    assert db_utils.get_drafts(pgsql, fields=['mission_id'], flatten=True) == [
        'mission_id' for _ in range(len(drafts))
    ]

    assert _mock_processing_create_event.times_called == 1

    assert db_utils.get_history(pgsql, fields=['type']) == [
        {'type': 'mission_created'},
    ]


async def test_idempotency(taxi_scooters_ops, mockserver):
    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def _mock_processing_create_event(request):
        assert request.headers['X-Idempotency-Token'] == 'created-mission_id'
        return {'event_id': 'idontcare'}

    request = copy.deepcopy(RECHARGE_2_SCOOTERS_REQUEST)

    response1 = await taxi_scooters_ops.post(
        HANDLER, request, params={'mission_id': 'mission_id'},
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER, request, params={'mission_id': 'mission_id'},
    )
    assert response2.status == 200
    assert response1.json() == response2.json()

    assert _mock_processing_create_event.times_called == 2


@pytest.mark.parametrize(
    ['request_body'],
    [
        pytest.param(
            {
                'performer_id': 'performer',
                'related_drafts': [],
                'points': [
                    {
                        'type': 'depot',
                        'location': [35.2, 42.6],
                        'typed_extra': {'warehouse_id': 'warehouse'},
                    },
                ],
            },
            id='Invalid Depot extra',
        ),
        pytest.param(
            {
                'performer_id': 'performer',
                'related_drafts': [],
                'points': [
                    {
                        'type': 'scooter',
                        'location': [35.2, 42.6],
                        'typed_extra': {'depot_id': 'depot'},
                    },
                ],
            },
            id='Invalid PointScooter extra',
        ),
    ],
)
async def test_bad_requests(taxi_scooters_ops, pgsql, request_body):
    response = await taxi_scooters_ops.post(
        HANDLER, request_body, params={'mission_id': 'mission_id'},
    )
    assert response.status == 400


async def test_related_drafts_conflict(taxi_scooters_ops, pgsql):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_1',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vehicle_1'},
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_2',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vehicle_2'},
            'mission_id': 'another_mission',
        },
    )

    request = copy.deepcopy(RECHARGE_2_SCOOTERS_REQUEST)
    request['related_drafts'] = ['draft_1', 'draft_2']

    response = await taxi_scooters_ops.post(
        HANDLER, request, params={'mission_id': 'mission_id'},
    )
    assert response.status == 409
    assert response.json() == {
        'code': 'conflict',
        'message': (
            'Drafts already connected to another '
            'missions or not found: [draft_2]'
        ),
    }


@pytest.mark.parametrize(
    'relation,expected_drafts',
    [
        pytest.param(
            'mission',
            [
                {
                    'draft_id': 'draft_1',
                    'job_id': None,
                    'mission_id': 'mission_id',
                    'point_id': None,
                },
                {
                    'draft_id': 'draft_2',
                    'job_id': None,
                    'mission_id': 'mission_id',
                    'point_id': None,
                },
            ],
            id='related mission',
        ),
        pytest.param(
            'points',
            [
                {
                    'draft_id': 'draft_1',
                    'job_id': None,
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
                {
                    'draft_id': 'draft_2',
                    'job_id': None,
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
            ],
            id='related points',
        ),
        pytest.param(
            'jobs',
            [
                {
                    'draft_id': 'draft_1',
                    'job_id': utils.AnyNotNoneValue(),
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
                {
                    'draft_id': 'draft_2',
                    'job_id': utils.AnyNotNoneValue(),
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
            ],
            id='related jobs',
        ),
        pytest.param(
            'point_job',
            [
                {
                    'draft_id': 'draft_1',
                    'job_id': None,
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
                {
                    'draft_id': 'draft_2',
                    'job_id': utils.AnyNotNoneValue(),
                    'mission_id': 'mission_id',
                    'point_id': utils.AnyNotNoneValue(),
                },
            ],
            id='related point and job',
        ),
    ],
)
async def test_drafts_relations(
        taxi_scooters_ops, pgsql, mockserver, relation, expected_drafts,
):
    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def _mock_processing_create_event(request):
        return {'event_id': 'idontcare'}

    for draft_id in ['draft_1', 'draft_2']:
        db_utils.add_draft(
            pgsql,
            {
                'draft_id': draft_id,
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'vehicle_1'},
            },
        )

    request = copy.deepcopy(RECHARGE_2_SCOOTERS_REQUEST)

    if relation == 'mission':
        request['related_drafts'] = ['draft_1', 'draft_2']
    elif relation == 'points':
        request['points'][0]['related_drafts'] = ['draft_1']
        request['points'][1]['related_drafts'] = ['draft_2']
    elif relation == 'jobs':
        request['points'][0]['jobs'][0]['related_drafts'] = ['draft_1']
        request['points'][1]['jobs'][0]['related_drafts'] = ['draft_2']
    elif relation == 'point_job':
        request['points'][0]['related_drafts'] = ['draft_1']
        request['points'][1]['jobs'][0]['related_drafts'] = ['draft_2']
    else:
        assert False, 'Bad relation'

    response = await taxi_scooters_ops.post(
        HANDLER, request, params={'mission_id': 'mission_id'},
    )
    assert response.status == 200
    assert (
        db_utils.get_drafts(
            pgsql, fields=['draft_id', 'mission_id', 'point_id', 'job_id'],
        )
        == expected_drafts
    )

    assert _mock_processing_create_event.times_called == 1


async def test_mixed_drafts_relations(taxi_scooters_ops, pgsql):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_1',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vehicle_1'},
        },
    )

    request = copy.deepcopy(RECHARGE_2_SCOOTERS_REQUEST)

    request['related_drafts'] = ['draft_1']
    request['points'][0]['related_drafts'] = ['draft_1']

    response = await taxi_scooters_ops.post(
        HANDLER, request, params={'mission_id': 'mission_id'},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'bad-draft-relation',
        'message': 'Draft: draft_1 relates to several entities',
    }
