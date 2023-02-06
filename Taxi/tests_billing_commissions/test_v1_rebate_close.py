import pytest


@pytest.mark.parametrize(
    'query, headers, status, expected_error, expected_close',
    [
        (  # normal close
            {
                'rules': ['2abf062a-b607-11ea-998e-07e60204cbcf'],
                'close_at': '2020-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            200,
            {},
            [('2abf062a-b607-11ea-998e-07e60204cbcf',)],
        ),
        (
            {
                'rules': ['2abf061a-b607-11ea-998e-07e60204cbcf'],
                'close_at': '2019-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            404,
            {'code': 'RULES_NOT_FOUND', 'message': 'Rules not found'},
            [],
        ),
        (
            {
                'rules': ['f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'],
                'close_at': '2031-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid rule start-end bounds',
            },
            [],
        ),
        (
            {
                'rules': ['f3a0503d-3f30-4a43-8e30-71d77ebcab1f'],
                'close_at': '2031-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid rule start-end bounds',
            },
            [],
        ),
        (
            {
                'rules': ['f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'],
                'close_at': '2021-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid rule start-end bounds',
            },
            [],
        ),
        (
            {
                'rules': ['f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'],
                'close_at': '2016-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Forbidden to close rules with a date in the past',
            },
            [],
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_close.sql'],
)
async def test_close_check(
        taxi_billing_commissions,
        query,
        headers,
        status,
        expected_error,
        expected_close,
        billing_commissions_postgres_db,
):
    response = await taxi_billing_commissions.post(
        'v1/rebate/close', json=query, headers=headers,
    )
    assert response.status_code == status
    response_json = response.json()
    if status != 200:
        assert expected_error == response_json
    billing_commissions_postgres_db.execute(
        'SELECT rule_id FROM fees.draft_rebate_rule_to_close',
    )
    rows = billing_commissions_postgres_db.fetchall()
    assert rows == expected_close
