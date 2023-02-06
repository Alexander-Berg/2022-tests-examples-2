import pytest


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'rule_id, expected_size, expected_names, expected_sources',
    [
        (0, 1, ['zero'], ['return 0;']),
        (1, 2, ['one', 'zero'], ['return 1;', 'return 0;']),
        (
            2,
            3,
            ['two', 'one', 'zero'],
            ['return 2;', 'return 1;', 'return 0;'],
        ),
        (
            5,
            6,
            ['five', 'four', 'three', 'two', 'one', 'zero'],
            [
                'return 5;',
                'return 4;',
                'return 3;',
                'return 2;',
                'return 1;',
                'return 0;',
            ],
        ),
    ],
    ids=['orphan', 'only child', 'two children', 'many children'],
)
async def test_v1_settings_history(
        taxi_pricing_admin,
        rule_id,
        expected_size,
        expected_names,
        expected_sources,
):
    response = await taxi_pricing_admin.get(
        'v1/settings/rule/history', params={'id': rule_id},
    )
    assert response.status_code == 200
    rules = response.json()['rules']
    assert len(rules) == expected_size
    for (rule, expected_name, expected_source) in zip(
            rules, expected_names, expected_sources,
    ):
        assert rule['name'] == expected_name
        assert rule['source_code'] == expected_source
