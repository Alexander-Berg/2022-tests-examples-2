import pytest

from tests_contractor_instant_payouts import utils

ENDPOINT = '/fleet/instant-payouts/v2/contractor-rules/by-ids/retrieve'

OK_PARAMS = [
    (
        'PARK-01',
        ['CONTRACTOR-01'],
        [
            {
                'contractor_id': 'CONTRACTOR-01',
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
        ],
    ),
    (
        'PARK-01',
        ['CONTRACTOR-01', 'CONTRACTOR-02'],
        [
            {
                'contractor_id': 'CONTRACTOR-01',
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
            {
                'contractor_id': 'CONTRACTOR-02',
                'rule_id': '00000000-0000-0000-0000-000000000002',
                'rule_name': 'Rule 2',
            },
        ],
    ),
    (
        'PARK-01',
        ['CONTRACTOR-01', 'CONTRACTOR-99'],
        [
            {
                'contractor_id': 'CONTRACTOR-01',
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
        ],
    ),
    ('PARK-01', ['CONTRACTOR-99'], []),
    ('PARK-02', ['CONTRACTOR-01'], []),
]


@pytest.mark.parametrize(
    'park_id, contractor_ids, expected_response_items', OK_PARAMS,
)
async def test_ok(
        taxi_contractor_instant_payouts,
        park_id,
        contractor_ids,
        expected_response_items,
):
    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT,
        headers=utils.build_headers(park_id=park_id),
        json={'contractor_ids': contractor_ids},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'items': expected_response_items}
