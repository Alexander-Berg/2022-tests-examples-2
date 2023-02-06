async def test_success(contractors_rules_list, stock, stq, pgsql):
    park_id = 'PARK-01'
    contractor_ids = ['CONTRACTOR-01', 'CONTRACTOR-02']

    response = await contractors_rules_list(
        park_id=park_id, contractor_ids=contractor_ids,
    )

    assert response.json() == {
        'items': [
            {
                'contractor_id': 'CONTRACTOR-01',
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
            {
                'contractor_id': 'CONTRACTOR-02',
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
        ],
    }
