import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils

HANDLER = '/scooters-ops/v1/drafts/create'


@pytest.mark.parametrize(
    'body,expected_response',
    [
        pytest.param(
            {'type': 'recharge', 'typed_extra': {'vehicle_id': 'v_id'}},
            {
                'id': 'draft_id',
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'v_id'},
                'mission_id': None,
                'status': 'pending',
                'revision': 1,
                'created_at': utils.AnyValue(),
            },
            id='recharge draft',
        ),
        pytest.param(
            {'type': 'resurrect', 'typed_extra': {'vehicle_id': 'v_id'}},
            {
                'id': 'draft_id',
                'type': 'resurrect',
                'typed_extra': {'vehicle_id': 'v_id'},
                'mission_id': None,
                'status': 'pending',
                'revision': 1,
                'created_at': utils.AnyValue(),
            },
            id='resurrect draft',
        ),
        pytest.param(
            {
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'v_id'},
                'expires_at': '2022-02-14T12:00:00+0300',
            },
            {
                'id': 'draft_id',
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'v_id'},
                'mission_id': None,
                'status': 'pending',
                'revision': 1,
                'created_at': utils.AnyValue(),
                'expires_at': '2022-02-14T09:00:00+00:00',
            },
            id='draft with expires_at',
        ),
    ],
)
async def test_handler(taxi_scooters_ops, stq, body, expected_response):
    response = await taxi_scooters_ops.post(
        HANDLER, body, params={'draft_id': 'draft_id'},
    )

    assert response.status == 200
    assert response.json() == {'draft': expected_response}
    assert stq.scooters_ops_process_draft.times_called == 2


async def test_repeat(taxi_scooters_ops, pgsql):
    request = {'type': 'recharge', 'typed_extra': {'vehicle_id': 'v_id'}}
    response_1 = await taxi_scooters_ops.post(
        HANDLER, request, params={'draft_id': 'draft_id'},
    )
    assert response_1.status == 200
    response_2 = await taxi_scooters_ops.post(
        HANDLER, request, params={'draft_id': 'draft_id'},
    )
    assert response_2.status == 200

    drafts = db_utils.get_drafts(
        pgsql, ['draft_id'], fields=['draft_id'], flatten=True,
    )
    assert drafts == ['draft_id']
