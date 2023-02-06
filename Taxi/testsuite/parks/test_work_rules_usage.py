import pytest

from . import error


def _make_ids(n: int):
    return [f'id{x}' for x in range(0, n)]


@pytest.mark.parametrize(
    ('park_id', 'work_rule_ids', 'work_rules'),
    [
        (
            '1488',
            ['rule_one', 'rule_two', 'rule_five'],
            [{'id': 'rule_one', 'usage': 5}, {'id': 'rule_two', 'usage': 4}],
        ),
        ('222333', ['rule_100500'], []),
        ('222333', _make_ids(100), []),
    ],
)
def test_ok(taxi_parks, park_id, work_rule_ids, work_rules):
    response = taxi_parks.post(
        '/v1/work-rules/usage',
        params={'park_id': park_id},
        json={'ids': work_rule_ids},
    )

    assert response.status_code == 200
    assert response.json() == {'work_rules': work_rules}


@pytest.mark.parametrize(
    ('park_id', 'work_rule_ids', 'expected_code', 'error_text'),
    [
        ('1488', [], 400, 'ids length must be between 1 and 100 items'),
        (
            '1488',
            _make_ids(101),
            400,
            'ids length must be between 1 and 100 items',
        ),
        ('unknown', ['rule_unknown'], 404, 'park not found'),
    ],
)
def test_fail(taxi_parks, park_id, work_rule_ids, expected_code, error_text):
    response = taxi_parks.post(
        '/v1/work-rules/usage',
        params={'park_id': park_id},
        json={'ids': work_rule_ids},
    )

    assert response.status_code == expected_code
    assert response.json() == error.make_error_response(error_text)
