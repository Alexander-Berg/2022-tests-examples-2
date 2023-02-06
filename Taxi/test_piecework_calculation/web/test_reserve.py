import datetime

import pytest

NOW = datetime.datetime(2022, 1, 20, 0, 0)


@pytest.mark.parametrize(
    'tariff_type, data, expected_status, expected_response',
    [
        ('support-taxi', {}, 400, None),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'some_branch',
                    'period_limit': 1000,
                    'initial_offset': 0,
                    'weekends_weight': 0,
                },
            },
            200,
            {
                'data': {
                    'reserve': {
                        'country': 'ru',
                        'branch': 'some_branch',
                        'period_limit': 1000,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                },
                'diff': {
                    'current': {},
                    'new': {
                        'country': 'ru',
                        'branch': 'some_branch',
                        'period_limit': 1000,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                },
            },
        ),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'existing_branch',
                    'period_limit': 1000,
                    'initial_offset': 0,
                    'weekends_weight': 0,
                },
            },
            200,
            {
                'data': {
                    'reserve': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 1000,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                },
                'diff': {
                    'current': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 500,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                    'new': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 1000,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                },
            },
        ),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'existing_branch',
                    'period_limit': 1000,
                    'initial_offset': 123.45,
                    'weekends_weight': 0.2,
                },
            },
            200,
            {
                'data': {
                    'reserve': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 1000,
                        'initial_offset': 123.45,
                        'weekends_weight': 0.2,
                    },
                },
                'diff': {
                    'current': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 500,
                        'initial_offset': 0,
                        'weekends_weight': 0,
                    },
                    'new': {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 1000,
                        'initial_offset': 123.45,
                        'weekends_weight': 0.2,
                    },
                },
            },
        ),
    ],
)
async def test_check(
        web_app_client,
        tariff_type,
        data,
        expected_status,
        expected_response,
        mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/reserve/{}/branch_settings/check'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == expected_response


@pytest.mark.parametrize(
    'tariff_type, data, expected_status, expected_pg_data',
    [
        ('support-taxi', {}, 400, None),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'some_branch',
                    'period_limit': 1000,
                    'initial_offset': 0,
                    'weekends_weight': 0,
                },
            },
            200,
            {'period_limit': 1000, 'initial_offset': 0, 'weekends_weight': 0},
        ),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'existing_branch',
                    'period_limit': 1000,
                    'initial_offset': 0,
                    'weekends_weight': 0,
                },
            },
            200,
            {'period_limit': 1000, 'initial_offset': 0, 'weekends_weight': 0},
        ),
        (
            'support-taxi',
            {
                'reserve': {
                    'country': 'ru',
                    'branch': 'existing_branch',
                    'period_limit': 1000,
                    'initial_offset': 123.45,
                    'weekends_weight': 0.2,
                },
            },
            200,
            {
                'period_limit': 1000,
                'initial_offset': 123.45,
                'weekends_weight': 0.2,
            },
        ),
    ],
)
async def test_apply(
        web_app_client,
        web_context,
        tariff_type,
        data,
        expected_status,
        expected_pg_data,
        mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/reserve/{}/branch_settings/apply'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_data = await conn.fetchrow(
            'SELECT period_limit, initial_offset, weekends_weight '
            'FROM piecework.branch_reserve '
            'WHERE tariff_type = $1 AND country = $2 AND branch = $3',
            tariff_type,
            data['reserve']['country'],
            data['reserve']['branch'],
        )
    assert dict(pg_data) == expected_pg_data


@pytest.mark.parametrize(
    'tariff_type, data, expected_status, expected_response',
    [
        ('support-taxi', {}, 400, None),
        (
            'support-taxi',
            {'country': 'ru', 'branch': 'existing_branch'},
            200,
            {'data': {'country': 'ru', 'branch': 'existing_branch'}},
        ),
        (
            'support-taxi',
            {'country': 'ru', 'branch': 'missing_branch'},
            409,
            None,
        ),
    ],
)
async def test_check_delete(
        web_app_client,
        tariff_type,
        data,
        expected_status,
        expected_response,
        mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/reserve/{}/branch_settings/check_delete'.format(tariff_type),
        json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == expected_response


@pytest.mark.parametrize(
    'tariff_type, data, expected_status',
    [
        ('support-taxi', {}, 400),
        ('support-taxi', {'country': 'ru', 'branch': 'existing_branch'}, 200),
        ('support-taxi', {'country': 'ru', 'branch': 'missing_branch'}, 200),
    ],
)
async def test_delete(
        web_app_client, web_context, tariff_type, data, expected_status,
):
    response = await web_app_client.post(
        '/v1/reserve/{}/branch_settings/delete'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == {}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_data = await conn.fetchrow(
            'SELECT COUNT(*) AS cnt '
            'FROM piecework.branch_reserve '
            'WHERE tariff_type = $1 AND country = $2 AND branch = $3',
            tariff_type,
            data['country'],
            data['branch'],
        )
        assert pg_data['cnt'] == 0


@pytest.mark.parametrize(
    'tariff_type, expected_response',
    [
        ('support-eats', {'branches': []}),
        (
            'support-taxi',
            {
                'branches': [
                    {
                        'country': 'ru',
                        'branch': '__default__',
                        'period_limit': 1500.0,
                        'initial_offset': 100.0,
                        'weekends_weight': 0.3,
                    },
                    {
                        'country': 'by',
                        'branch': '__default__',
                        'period_limit': 1000.0,
                        'initial_offset': 200.0,
                        'weekends_weight': 0.2,
                    },
                    {
                        'country': 'ru',
                        'branch': 'existing_branch',
                        'period_limit': 500.0,
                        'initial_offset': 0.0,
                        'weekends_weight': 0.0,
                    },
                    {
                        'country': 'ru',
                        'branch': 'other_branch',
                        'period_limit': 1500.0,
                        'initial_offset': 100.0,
                        'weekends_weight': 0.3,
                    },
                ],
            },
        ),
    ],
)
async def test_list(web_app_client, tariff_type, expected_response):
    response = await web_app_client.get(
        '/v1/reserve/{}/branch_settings/list'.format(tariff_type),
    )
    assert response.status == 200

    content = await response.json()
    assert content == expected_response


@pytest.mark.config(PIECEWORK_CALCULATION_DEFAULT_RESERVE_INITIAL_OFFSET=123.0)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'logins, disable_default, expected_response',
    [
        (
            ['ivanov', 'petrov'],
            None,
            {
                'logins': [
                    {
                        'login': 'ivanov',
                        'value': 147.33333333333334,
                        'updated': '2022-02-01T03:00:00+03:00',
                    },
                    {
                        'login': 'petrov',
                        'value': 100,
                        'updated': '2022-01-16T03:00:00+03:00',
                    },
                ],
            },
        ),
        (
            ['ivanov', 'petrov', 'smirnoff', 'popov'],
            None,
            {
                'logins': [
                    {
                        'login': 'ivanov',
                        'value': 147.33333333333334,
                        'updated': '2022-02-01T03:00:00+03:00',
                    },
                    {
                        'login': 'petrov',
                        'value': 100,
                        'updated': '2022-01-16T03:00:00+03:00',
                    },
                    {'login': 'popov', 'value': 100.0},
                    {'login': 'smirnoff', 'value': 123.0},
                ],
            },
        ),
        (
            ['ivanov', 'petrov', 'smirnoff', 'popov'],
            True,
            {
                'logins': [
                    {
                        'login': 'ivanov',
                        'value': 147.33333333333334,
                        'updated': '2022-02-01T03:00:00+03:00',
                    },
                    {
                        'login': 'petrov',
                        'value': 100,
                        'updated': '2022-01-16T03:00:00+03:00',
                    },
                    {'login': 'popov', 'value': 100.0},
                ],
            },
        ),
        (
            ['smirnoff', 'popov'],
            None,
            {
                'logins': [
                    {'login': 'popov', 'value': 100.0},
                    {'login': 'smirnoff', 'value': 123.0},
                ],
            },
        ),
        (
            ['stahanov'],
            None,
            {
                'logins': [
                    {
                        'login': 'stahanov',
                        'value': 16.25,
                        'updated': '2022-02-01T03:00:00+03:00',
                    },
                ],
            },
        ),
        (['kotov'], None, {'logins': [{'login': 'kotov', 'value': 200}]}),
        (
            ['smirnov'],
            None,
            {
                'logins': [
                    {
                        'login': 'smirnov',
                        'value': 125,
                        'updated': '2022-02-01T03:00:00+03:00',
                    },
                ],
            },
        ),
        (
            ['old_login'],
            None,
            {'logins': [{'login': 'old_login', 'value': 50}]},
        ),
    ],
)
async def test_current(
        web_app_client, logins, disable_default, expected_response,
):
    response = await web_app_client.post(
        '/v1/reserve/current',
        json={'logins': logins, 'disable_default': disable_default},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
