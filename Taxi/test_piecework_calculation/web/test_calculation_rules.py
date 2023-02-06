import datetime

import pytest

NOW = datetime.datetime(2020, 1, 1, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_response',
    [
        # Empty data
        ({}, 400, None),
        # Invalid data
        ({'rule': {'wrong': 'rule'}}, 400, None),
        # stop_date less then start_date
        (
            {
                'rule': {
                    'start_date': '2020-02-01',
                    'stop_date': '2020-01-16',
                    'repeat': True,
                    'countries': ['rus', 'blr'],
                },
            },
            409,
            None,
        ),
        # All OK
        (
            {
                'rule': {
                    'start_date': '2020-01-16',
                    'stop_date': '2020-02-01',
                    'repeat': True,
                    'countries': ['rus', 'blr'],
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'some_uuid',
                        'start_date': '2020-01-16',
                        'stop_date': '2020-02-01',
                        'countries': ['rus', 'blr'],
                        'repeat': True,
                    },
                },
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                    'repeat': False,
                    'countries': ['kaz'],
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'some_uuid',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['kaz'],
                    },
                },
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                    'repeat': False,
                    'countries': ['usa'],
                    'logins': ['some', 'users'],
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'some_uuid',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'logins': ['some', 'users'],
                    },
                },
            },
        ),
    ],
)
async def test_check(
        web_app_client, data, expected_status, expected_response, mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/check', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_pg_result',
    [
        # Empty data
        ({}, 400, None),
        # Invalid data
        ({'rule': {'wrong': 'rule'}}, 400, None),
        # No rule id
        (
            {
                'rule': {
                    'start_date': '2020-01-16',
                    'stop_date': '2020-02-01',
                    'countries': ['rus', 'blr'],
                    'repeat': True,
                },
            },
            400,
            None,
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'new_rule_id',
                    'start_date': '2020-01-16',
                    'stop_date': '2020-02-01',
                    'countries': ['rus', 'blr'],
                    'repeat': True,
                },
            },
            200,
            {
                'calculation_rule_id': 'new_rule_id',
                'tariff_type': 'support-taxi',
                'start_date': datetime.date(2020, 1, 16),
                'stop_date': datetime.date(2020, 2, 1),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': True,
                'status': 'waiting_agent',
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'new_rule_id',
                    'start_date': '2020-01-16',
                    'stop_date': '2020-02-01',
                    'countries': ['rus', 'blr'],
                    'logins': ['some', 'logins'],
                    'repeat': True,
                },
            },
            200,
            {
                'calculation_rule_id': 'new_rule_id',
                'tariff_type': 'support-taxi',
                'start_date': datetime.date(2020, 1, 16),
                'stop_date': datetime.date(2020, 2, 1),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': ['some', 'logins'],
                'enabled': True,
                'status': 'waiting_agent',
                'description': '',
            },
        ),
    ],
)
async def test_create(
        web_context, web_app_client, data, expected_status, expected_pg_result,
):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/create', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT '
            'calculation_rule_id, tariff_type, start_date, stop_date, repeat, '
            'countries, logins, enabled, status, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            data['rule']['calculation_rule_id'],
        )

    assert dict(pg_result) == expected_pg_result


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_response',
    [
        # Empty data
        ({}, 400, None),
        # Invalid data
        ({'rule': {'wrong': 'rule'}}, 400, None),
        # Missing rule
        ({'rule': {'calculation_rule_id': 'missing_rule_id'}}, 404, None),
        # stop_date less then start_date
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'start_date': '2020-02-01',
                },
            },
            409,
            None,
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'repeat': False,
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'periodic_rule_id',
                        'repeat': False,
                    },
                },
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'enabled': False,
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'periodic_rule_id',
                        'enabled': False,
                    },
                },
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'start_date': '2020-02-01',
                    'stop_date': '2020-02-16',
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'periodic_rule_id',
                        'start_date': '2020-02-01',
                        'stop_date': '2020-02-16',
                    },
                },
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'logins': ['some', 'users'],
                },
            },
            200,
            {
                'data': {
                    'rule': {
                        'calculation_rule_id': 'periodic_rule_id',
                        'logins': ['some', 'users'],
                    },
                },
            },
        ),
    ],
)
async def test_check_update(
        web_app_client, data, expected_status, expected_response, mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/check_update', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_pg_result',
    [
        # Empty data
        ({}, 400, None),
        # Invalid data
        ({'rule': {'wrong': 'rule'}}, 400, None),
        # Missing rule
        ({'rule': {'calculation_rule_id': 'missing_rule_id'}}, 404, None),
        # No rule id
        (
            {
                'rule': {
                    'start_date': '2020-01-16',
                    'stop_date': '2020-02-01',
                    'countries': ['rus', 'blr'],
                    'repeat': True,
                },
            },
            400,
            None,
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'repeat': False,
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': False,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': True,
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'enabled': False,
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': False,
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'countries': ['rus'],
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus'],
                'logins': None,
                'enabled': True,
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'logins': ['ivanov', 'petrov'],
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': ['ivanov', 'petrov'],
                'enabled': True,
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'start_date': '2020-02-01',
                    'stop_date': '2020-02-16',
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 2, 1),
                'stop_date': datetime.date(2020, 2, 16),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': True,
                'description': '',
            },
        ),
        # All OK
        (
            {
                'rule': {
                    'calculation_rule_id': 'periodic_rule_id',
                    'description': 'test',
                },
            },
            200,
            {
                'calculation_rule_id': 'periodic_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': True,
                'description': 'test',
            },
        ),
    ],
)
async def test_update(
        web_context, web_app_client, data, expected_status, expected_pg_result,
):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/update', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, repeat, '
            'countries, logins, enabled, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            data['rule']['calculation_rule_id'],
        )
    assert dict(pg_result) == expected_pg_result


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status',
    [
        # Empty data
        ({}, 400),
        # Invalid data
        ({'wrong': 'rule'}, 400),
        # Missing rule
        ({'calculation_rule_id': 'missing_rule_id'}, 404),
        # All OK
        ({'calculation_rule_id': 'periodic_rule_id'}, 200),
    ],
)
async def test_check_delete(web_app_client, data, expected_status, mock_uuid4):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/check_delete', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {'data': data}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status',
    [
        # Empty data
        ({}, 400),
        # Invalid data
        ({'wrong': 'rule'}, 400),
        # Missing rule
        ({'calculation_rule_id': 'missing_rule_id'}, 404),
        # All OK
        ({'calculation_rule_id': 'periodic_rule_id'}, 200),
    ],
)
async def test_delete(web_context, web_app_client, data, expected_status):
    response = await web_app_client.post(
        '/v1/calculation_rules/support-taxi/delete', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT COUNT(*) AS cnt '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            data['calculation_rule_id'],
        )
    assert pg_result['cnt'] == 0


@pytest.mark.parametrize(
    ['calculation_rule_id', 'expected_status', 'expected_response'],
    [
        (
            'other_logins_rule_id',
            200,
            {
                'rule': {
                    'calculation_rule_id': 'other_logins_rule_id',
                    'countries': ['usa'],
                    'enabled': True,
                    'logins': ['other', 'logins'],
                    'repeat': False,
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                    'status': 'waiting_agent',
                    'tariff_type': 'support-taxi',
                    'payment_draft_ids': {},
                },
            },
        ),
        (
            'success_rule_id',
            200,
            {
                'rule': {
                    'calculation_rule_id': 'success_rule_id',
                    'countries': ['rus'],
                    'enabled': True,
                    'repeat': False,
                    'start_date': '2019-12-16',
                    'stop_date': '2020-01-01',
                    'status': 'success',
                    'tariff_type': 'support-taxi',
                    'payment_draft_ids': {'rus': 12345},
                },
            },
        ),
        ('missing_rule_id', 404, None),
    ],
)
async def test_get_calculation_rule(
        web_app_client,
        calculation_rule_id,
        expected_status,
        expected_response,
):
    response = await web_app_client.get(
        '/v1/calculation_rule/support-taxi/{}'.format(calculation_rule_id),
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    ['data', 'expected_response'],
    [
        (
            {},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                    {
                        'calculation_rule_id': 'success_rule_id',
                        'countries': ['rus'],
                        'enabled': True,
                        'repeat': False,
                        'start_date': '2019-12-16',
                        'stop_date': '2020-01-01',
                        'status': 'success',
                        'tariff_type': 'support-taxi',
                        'payment_draft_ids': {'rus': 12345},
                    },
                ],
            },
        ),
        (
            {'period_date': '2020-01-01'},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        (
            {'period_date': '2019-12-31'},
            {
                'rules': [
                    {
                        'calculation_rule_id': 'success_rule_id',
                        'countries': ['rus'],
                        'enabled': True,
                        'repeat': False,
                        'start_date': '2019-12-16',
                        'stop_date': '2020-01-01',
                        'status': 'success',
                        'tariff_type': 'support-taxi',
                        'payment_draft_ids': {'rus': 12345},
                    },
                ],
            },
        ),
        ({'period_date': '2020-01-16'}, {'rules': []}),
        (
            {'country': 'rus'},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'calculation_rule_id': 'success_rule_id',
                        'countries': ['rus'],
                        'enabled': True,
                        'repeat': False,
                        'start_date': '2019-12-16',
                        'stop_date': '2020-01-01',
                        'status': 'success',
                        'tariff_type': 'support-taxi',
                        'payment_draft_ids': {'rus': 12345},
                    },
                ],
            },
        ),
        (
            {'country': 'usa'},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        ({'country': 'aze'}, {'rules': []}),
        (
            {'login': 'other'},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        ({'login': 'wrong'}, {'rules': []}),
        (
            {'status': 'waiting_agent'},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        ({'status': 'error'}, {'rules': []}),
        (
            {'enabled': True},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                    {
                        'calculation_rule_id': 'success_rule_id',
                        'countries': ['rus'],
                        'enabled': True,
                        'repeat': False,
                        'start_date': '2019-12-16',
                        'stop_date': '2020-01-01',
                        'status': 'success',
                        'tariff_type': 'support-taxi',
                        'payment_draft_ids': {'rus': 12345},
                    },
                ],
            },
        ),
        ({'enabled': False}, {'rules': []}),
        (
            {'repeat': True},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': True,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'periodic_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        (
            {'repeat': False},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['rus', 'blr'],
                        'calculation_rule_id': 'rus_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'payment_draft_ids': {},
                    },
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                    {
                        'calculation_rule_id': 'success_rule_id',
                        'countries': ['rus'],
                        'enabled': True,
                        'repeat': False,
                        'start_date': '2019-12-16',
                        'stop_date': '2020-01-01',
                        'status': 'success',
                        'tariff_type': 'support-taxi',
                        'payment_draft_ids': {'rus': 12345},
                    },
                ],
            },
        ),
        (
            {'older_than': 'periodic_rule_id', 'limit': 1},
            {
                'rules': [
                    {
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'repeat': False,
                        'countries': ['usa'],
                        'calculation_rule_id': 'other_logins_rule_id',
                        'tariff_type': 'support-taxi',
                        'status': 'waiting_agent',
                        'enabled': True,
                        'logins': ['other', 'logins'],
                        'payment_draft_ids': {},
                    },
                ],
            },
        ),
        ({'older_than': 'success_rule_id', 'limit': 1}, {'rules': []}),
    ],
)
async def test_calculation_rules_list(web_app_client, data, expected_response):
    response = await web_app_client.post(
        '/v1/calculation_rules/list', json=data,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response
