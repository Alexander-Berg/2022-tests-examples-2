import pytest


@pytest.mark.parametrize(
    'query_json, status, expected_message, expected_draft_records,'
    ' expected_draft_accounts',
    [
        ('request.json', 200, None, 1, 1),
        ('request_hiring.json', 200, None, 1, 1),
        ('request_many_accounts.json', 200, None, 1, 2),
        ('request_no_accounts.json', 200, None, 1, 0),
        ('request_no_end.json', 200, None, 1, 1),
        (
            'request_no_create.json',
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'Category with same kind already exists',
            },
            0,
            0,
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_categories_create.sql'],
)
async def test_create_check(
        taxi_billing_commissions,
        load_json,
        query_json,
        status,
        expected_message,
        billing_commissions_postgres_db,
        expected_draft_records,
        expected_draft_accounts,
):
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v1/categories/create', json=query,
    )
    assert response.status_code == status
    if status != 200:
        assert expected_message == response.json()
    else:
        _check_rows_exists(
            'SELECT id FROM fees.draft_category',
            billing_commissions_postgres_db,
            expected_draft_records,
        )
        _check_rows_exists(
            'SELECT id FROM fees.draft_category_account',
            billing_commissions_postgres_db,
            expected_draft_accounts,
        )


def _check_rows_exists(query, db, count):
    db.execute(query)
    rows = db.fetchall()
    assert len(rows) == count


@pytest.mark.parametrize(
    'query_json, status, expected_message, expected_draft_records',
    [('request.json', 200, None, [])],
)
@pytest.mark.now('2019-01-01T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['test_rules_v1_categories_create_approve.sql'],
)
async def test_create_approve(
        taxi_billing_commissions,
        load_json,
        query_json,
        status,
        expected_message,
        billing_commissions_postgres_db,
        expected_draft_records,
):
    headers = {
        'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
        'X-Yandex-Login': 'author',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Id': 'draft_id',
    }
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v1/categories/create/approve', json=query, headers=headers,
    )
    assert response.status_code == status
    if status != 200:
        assert expected_message == response.json()
    else:
        billing_commissions_postgres_db.execute(
            'SELECT draft_spec_id, id FROM fees.category '
            'where draft_spec_id = {draft_spec_id:d}'.format(
                draft_spec_id=query['draft_id'],
            ),
        )
        rows = billing_commissions_postgres_db.fetchall()
        # check category exists
        print(rows)
        assert rows
        billing_commissions_postgres_db.execute(
            'SELECT count(*) FROM fees.category_account where '
            'category_id = any(array[{category_id}]::uuid[])'.format(
                category_id='\'{}\''.format(
                    '\',\''.join([row[1] for row in rows]),
                ),
            ),
        )
        # check accounts creation
        assert billing_commissions_postgres_db.fetchall()[0][0] > 0
