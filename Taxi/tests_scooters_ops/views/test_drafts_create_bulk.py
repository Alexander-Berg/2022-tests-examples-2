import pytest

from tests_scooters_ops import db_utils

HANDLER = '/scooters-ops/v1/drafts/create-bulk'


@pytest.mark.parametrize('draft_type', ['recharge', 'resurrect'])
async def test_handler(taxi_scooters_ops, pgsql, stq, draft_type):
    request = {
        'drafts': [
            {
                'id': 'draft_id1',
                'type': draft_type,
                'typed_extra': {'vehicle_id': 'v_id'},
            },
            {
                'id': 'draft_id2',
                'type': draft_type,
                'typed_extra': {'vehicle_id': 'v_id'},
            },
        ],
    }
    response = await taxi_scooters_ops.post(HANDLER, request)

    assert response.status == 200
    assert stq.scooters_ops_process_draft.times_called == 4

    drafts = db_utils.get_drafts(pgsql, fields=['draft_id'], flatten=True)
    assert drafts == ['draft_id1', 'draft_id2']


async def test_repeat(taxi_scooters_ops, pgsql, stq):
    request = {
        'drafts': [
            {
                'id': 'draft_id1',
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'v_id'},
            },
            {
                'id': 'draft_id2',
                'type': 'resurrect',
                'typed_extra': {'vehicle_id': 'v_id'},
            },
        ],
    }

    response_1 = await taxi_scooters_ops.post(HANDLER, request)
    assert response_1.status == 200
    assert stq.scooters_ops_process_draft.times_called == 4

    response_2 = await taxi_scooters_ops.post(HANDLER, request)
    assert response_2.status == 200
    assert stq.scooters_ops_process_draft.times_called == 4  # no new stq's

    drafts = db_utils.get_drafts(pgsql, fields=['draft_id'], flatten=True)
    assert drafts == ['draft_id1', 'draft_id2']
