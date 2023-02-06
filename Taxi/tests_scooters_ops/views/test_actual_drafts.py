import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/drafts/actual'
TIME_NOW = '2022-05-10T12:00:00+0000'


@pytest.mark.parametrize(
    'drafts,expected_response',
    [
        pytest.param(
            [
                {
                    'draft_id': 'draft_01',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid'},
                    'status': 'actual',
                },
            ],
            {
                'drafts': [
                    {
                        'id': 'draft_01',
                        'type': 'recharge',
                        'typed_extra': {'vehicle_id': 'vid'},
                        'created_at': utils.AnyValue(),
                        'mission_id': None,
                        'status': 'actual',
                        'revision': 1,
                    },
                ],
            },
            id='has actual drafts',
        ),
        pytest.param(
            [
                {
                    'draft_id': 'draft_01',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid'},
                    'status': 'actual',
                },
                {
                    'draft_id': 'draft_02',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid2'},
                    'mission_id': 'mission',
                    'status': 'actual',
                    'revision': 1,
                },
            ],
            {
                'drafts': [
                    {
                        'id': 'draft_01',
                        'type': 'recharge',
                        'typed_extra': {'vehicle_id': 'vid'},
                        'created_at': utils.AnyValue(),
                        'mission_id': None,
                        'status': 'actual',
                        'revision': 1,
                    },
                ],
            },
            id='has one draft with mission',
        ),
        pytest.param(
            [
                {
                    'draft_id': 'draft_01',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid'},
                    'status': 'actual',
                    'expires_at': '2022-04-10T12:00:00+0000',
                },
            ],
            {'drafts': []},
            id='draft expired',
        ),
        pytest.param(
            [
                {
                    'draft_id': 'draft_01',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid'},
                    'status': 'actual',
                    'expires_at': '2022-06-10T12:00:00+0000',
                },
            ],
            {
                'drafts': [
                    {
                        'id': 'draft_01',
                        'type': 'recharge',
                        'typed_extra': {'vehicle_id': 'vid'},
                        'created_at': utils.AnyValue(),
                        'mission_id': None,
                        'status': 'actual',
                        'revision': 1,
                        'expires_at': '2022-06-10T12:00:00+00:00',
                    },
                ],
            },
            id='has expiration date but not expired',
        ),
        pytest.param(
            [
                {
                    'draft_id': 'draft_01',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid'},
                    'status': 'actual',
                    'expires_at': '2022-05-10T15:01:00+0300',  # now + 1min
                },
                {
                    'draft_id': 'draft_02',
                    'type': 'recharge',
                    'typed_extra': {'vehicle_id': 'vid2'},
                    'status': 'actual',
                    'expires_at': '2022-05-10T14:59:00+0300',  # now - 1min
                },
            ],
            {
                'drafts': [
                    {
                        'id': 'draft_01',
                        'type': 'recharge',
                        'typed_extra': {'vehicle_id': 'vid'},
                        'created_at': utils.AnyValue(),
                        'mission_id': None,
                        'status': 'actual',
                        'revision': 1,
                        'expires_at': '2022-05-10T12:01:00+00:00',
                    },
                ],
            },
            id='test timezone',
        ),
    ],
)
@pytest.mark.now(TIME_NOW)
async def test_handler(taxi_scooters_ops, pgsql, drafts, expected_response):
    for draft in drafts:
        db_utils.add_draft(pgsql, draft)

    resp = await taxi_scooters_ops.get(HANDLER)

    assert resp.status == 200
    assert resp.json() == expected_response
