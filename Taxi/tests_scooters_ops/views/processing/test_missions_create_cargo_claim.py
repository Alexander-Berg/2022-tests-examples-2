import copy
import typing

import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils


HANDLER = '/scooters-ops/v1/processing/missions/create-cargo-claim'

SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'status': 'created',
    'performer_id': 'dbid_uuid',
    'revision': 1,
    'points': [
        {
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'address': 'Вот в это место надо приехать',
        },
        {
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_id', 'number': 'scooter_number'},
            },
            'address': 'Вот в это место надо приехать',
        },
        {
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'address': 'Вот в это место надо приехать',
        },
    ],
    'tags': ['recharge'],
}


def create_mission_with_tags(tags: typing.List[str]) -> dict:
    copy_ = copy.deepcopy(SIMPLE_MISSION)
    copy_['tags'] = tags
    return copy_


@common.TRANSLATIONS
@pytest.mark.config(
    SCOOTERS_OPS_FLOW_RELATED_MISSION_TAGS=['recharge', 'relocate'],
)
async def test_handler(taxi_scooters_ops, pgsql, mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create-accepted',
    )
    async def _claims_create(request):
        expected_request = load_json('expected_cargo_request.json')
        for point in expected_request['claim']['route_points']:
            point[
                'external_order_id'
            ] = f'missions/{SIMPLE_MISSION["mission_id"]}'
        assert request.json == expected_request
        assert request.headers['Authorization'] == 'Bearer cargo_token'
        return load_json('cargo_response.json')

    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )

    assert response.status == 200

    mission = response.json()['mission']
    assert mission['cargo_claim_id'] == 'claim_id'
    assert [point['cargo_point_id'] for point in mission['points']] == [
        '847829',
        '847830',
        '847831',
    ]

    assert _claims_create.times_called == 1


@common.TRANSLATIONS
@pytest.mark.config(
    SCOOTERS_OPS_FLOW_RELATED_MISSION_TAGS=['recharge', 'relocate'],
)
async def test_idempotency(taxi_scooters_ops, pgsql, mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create-accepted',
    )
    async def _claims_create(request):
        expected_request = load_json('expected_cargo_request.json')
        for point in expected_request['claim']['route_points']:
            point[
                'external_order_id'
            ] = f'missions/{SIMPLE_MISSION["mission_id"]}'
        assert request.headers['Authorization'] == 'Bearer cargo_token'
        assert request.json == expected_request
        return load_json('cargo_response.json')

    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )
    assert response2.status == 200

    assert _claims_create.times_called == 1


async def test_not_found(taxi_scooters_ops):
    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'absent_mission_id', 'mission_revision': 1},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not-found',
        'message': 'mission: absent_mission_id not found',
    }


async def test_conflict_revision(taxi_scooters_ops, pgsql):
    db_utils.add_mission(
        pgsql,
        {'mission_id': 'mission_id', 'status': 'created', 'revision': 2},
    )

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'mission_id', 'mission_revision': 3},
    )

    assert response.status == 409
    assert response.json() == {
        'code': 'conflict',
        'message': 'Mission has revision: 2 but 3 requested',
    }


@common.TRANSLATIONS
@pytest.mark.config(
    SCOOTERS_OPS_FLOW_RELATED_MISSION_TAGS=['recharge', 'relocate', 'repair'],
)
@pytest.mark.parametrize(
    'mission, expected_comment',
    [
        pytest.param(
            SIMPLE_MISSION,  # mission
            'Миссия на перезарядку самокатов',  # expected_comment
            id='recharge_comment',
        ),
        pytest.param(
            create_mission_with_tags(['relocate']),  # mission
            'Миссия на релокацию самокатов',  # expected_comment
            id='relocation_comment',
        ),
        pytest.param(
            create_mission_with_tags(['repair']),  # mission
            'Миссия на ремонт самокатов',  # expected_comment
            id='repair_comment',
        ),
        pytest.param(
            create_mission_with_tags(
                ['recharge', 'relocate', 'repair'],
            ),  # mission
            'Смешанная миссия: перезарядка, релокация, ремонт',
            # expected_comment
            id='mixed_mission',
        ),
        pytest.param(
            create_mission_with_tags([]),  # mission
            None,  # expected_comment
            id='no_tags_mission',
        ),
        pytest.param(
            create_mission_with_tags(
                ['recharge', 'relocate', 'repair'],
            ),  # mission
            None,  # expected_comment
            marks=[
                pytest.mark.config(SCOOTERS_OPS_FLOW_RELATED_MISSION_TAGS=[]),
            ],
            id='no_flow_related_tags_in_config',
        ),
        pytest.param(
            create_mission_with_tags(
                ['recharge', 'relocate', 'repair'],
            ),  # mission
            'Смешанная миссия: перезарядка, релокация',  # expected_comment
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_FLOW_RELATED_MISSION_TAGS=[
                        'recharge',
                        'relocate',
                    ],
                ),
            ],
            id='only_some_tags_are_flow_related',
        ),
    ],
)
async def test_comment(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        load_json,
        mission,
        expected_comment,
):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create-accepted',
    )
    async def _claims_create(request):
        if expected_comment is not None:
            assert request.json['claim']['comment'] == expected_comment
        else:
            assert 'comment' not in request.json['claim']

        return load_json('cargo_response.json')

    db_utils.add_mission(pgsql, mission)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {},
        params={'mission_id': 'mission_id', 'mission_revision': 1},
    )

    assert response.status == 200

    assert _claims_create.times_called == 1
