from dateutil import parser
import pytest


@pytest.mark.parametrize(
    'query, headers, status, expected_error, expected_close',
    [
        (  # normal close
            {
                '_id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'close_at': '2020-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-Yandex-Login': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            200,
            {},
            [('2abf062a-b607-11ea-998e-07e60204cbcf',)],
        ),
        (
            {
                '_id': '2abf061a-b607-11ea-998e-07e60204cbcf',
                'close_at': '2018-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-Yandex-Login': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            404,
            {'code': 'RULES_NOT_FOUND', 'message': 'Rule not found'},
            [],
        ),
        (
            {
                '_id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                'close_at': '2031-01-01T18:48:00.000000+03:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-Yandex-Login': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Object has incorrect start-end bounds'
                    ': rule ends before close'
                ),
            },
            [],
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v2_rules_close.sql'],
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
        'v2/rules/close', json=query,
    )
    assert response.status_code == status
    response_json = response.json()
    if status != 200:
        assert expected_error == response_json
    else:
        assert response_json['data'].get('draft_id') is not None
    billing_commissions_postgres_db.execute(
        'SELECT rule_id FROM fees.draft_rule_to_close',
    )
    rows = billing_commissions_postgres_db.fetchall()
    assert rows == expected_close


@pytest.mark.parametrize(
    'query, headers, status, expected_response, expected_close',
    [
        (  # normal close
            {
                'draft_id': 4,
                '_id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'close_at': '2020-01-01T00:00:00+00:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-Yandex-Login': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            200,
            {},
            parser.parse('2020-01-01T00:00:00+00:00'),
        ),
        (
            {
                'draft_id': 5,
                '_id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'close_at': '2031-01-01T00:00:00+00:00',
            },
            {
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-Yandex-Login': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Object has incorrect start-end bounds'
                    ': rule ends before close'
                ),
            },
            None,
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v2_rules_close_approve.sql'],
)
async def test_close_approve(
        taxi_billing_commissions,
        query,
        headers,
        status,
        expected_response,
        expected_close,
        billing_commissions_postgres_db,
):
    response = await taxi_billing_commissions.post(
        'v2/rules/close/approve', json=query, headers=headers,
    )
    assert response.status_code == status
    if status != 200:
        assert expected_response == response.json()
    else:
        billing_commissions_postgres_db.execute(
            'SELECT ends_at FROM fees.rule where id = %(id)s',
            {'id': query['_id']},
        )
        rows = billing_commissions_postgres_db.fetchall()
        assert rows[0][0] == expected_close
