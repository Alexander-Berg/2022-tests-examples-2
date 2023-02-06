import datetime

import pytest

NOW = datetime.datetime(2020, 1, 1, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'tariff_type,data,expected_status,expected_response',
    [
        # Empty tariff
        ('support-taxi', {}, 400, None),
        # Invalid tariff data
        ('support-taxi', {'wrong': 'tariff'}, 400, None),
        # Tariff starts before today + two weeks
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2020-01-10',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '07:30:00',
                    'daytime_ends': '21:30:00',
                },
            },
            409,
            None,
        ),
        # No changes
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2022-01-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '123.45'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '321.00'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '07:30:00',
                    'daytime_ends': '21:30:00',
                },
            },
            409,
            None,
        ),
        # Tariff starts before actual tariff
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2020-04-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '07:30:00',
                    'daytime_ends': '21:30:00',
                },
            },
            409,
            None,
        ),
        # daytime_begins/ends must be specified
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                },
            },
            409,
            None,
        ),
        # invalid daytime_ends
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '08:00:00',
                    'daytime_ends': '25:00:00',
                },
            },
            400,
            None,
        ),
        # All OK
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': False,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                },
            },
            200,
            {
                'data': {
                    'tariff': {
                        'tariff_id': 'some_uuid',
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': False,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                    },
                },
                'diff': {
                    'current': {
                        'start_date': '2021-01-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '123.45'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '321.00'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                    'new': {
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': False,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                    },
                },
            },
        ),
        # All OK
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '08:00:00',
                    'daytime_ends': '20:00:00',
                },
            },
            200,
            {
                'data': {
                    'tariff': {
                        'tariff_id': 'some_uuid',
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'daytime_begins': '08:00:00',
                        'daytime_ends': '20:00:00',
                    },
                },
                'diff': {
                    'current': {
                        'start_date': '2021-01-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '123.45'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '321.00'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                    'new': {
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'daytime_begins': '08:00:00',
                        'daytime_ends': '20:00:00',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
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
        '/v1/tariffs/{}/check'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_status != 200:
        return

    assert content == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('piecework_calculation', files=[])
@pytest.mark.parametrize(
    'tariff_type,data,expected_status,expected_response',
    [
        # All OK
        (
            'support-taxi',
            {
                'tariff': {
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '08:00:00',
                    'daytime_ends': '20:00:00',
                },
            },
            200,
            {
                'data': {
                    'tariff': {
                        'tariff_id': 'some_uuid',
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'daytime_begins': '08:00:00',
                        'daytime_ends': '20:00:00',
                    },
                },
                'diff': {
                    'current': {},
                    'new': {
                        'start_date': '2021-05-01',
                        'cost_conditions': {
                            'rules': [
                                {'cost_by_line': {'some_line': '456.78'}},
                            ],
                        },
                        'benefit_conditions': {
                            '__default__': {'benefits': '654.32'},
                        },
                        'daytime_begins': '08:00:00',
                        'daytime_ends': '20:00:00',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                    },
                },
            },
        ),
    ],
)
async def test_check_first(
        web_app_client,
        tariff_type,
        data,
        expected_status,
        expected_response,
        mock_uuid4,
):
    response = await web_app_client.post(
        '/v1/tariffs/{}/check'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_status != 200:
        return

    assert content == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'tariff_type,data,expected_status,expected_pg_result,'
    'expected_old_tariff_stop_date',
    [
        ('support-taxi', {}, 400, None, None),
        ('support-taxi', {'wrong': 'tariff'}, 400, None, None),
        (
            'support-taxi',
            {
                'tariff': {
                    'tariff_id': 'new_tariff_id',
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': False,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                },
            },
            200,
            {
                'tariff_id': 'new_tariff_id',
                'tariff_type': 'support-taxi',
                'start_date': datetime.date(2021, 5, 1),
                'stop_date': datetime.date(9999, 12, 31),
                'cost_conditions': (
                    '{"rules": [{"cost_by_line": {"some_line": "456.78"}}]}'
                ),
                'benefit_conditions': (
                    '{"__default__": {"benefits": "654.32"}}'
                ),
                'countries': ['rus', 'blr'],
                'calc_night': False,
                'calc_holidays': True,
                'calc_workshifts': True,
                'daytime_begins': None,
                'daytime_ends': None,
            },
            datetime.date(2021, 5, 1),
        ),
        (
            'support-taxi',
            {
                'tariff': {
                    'tariff_id': 'new_tariff_id',
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['rus', 'blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '08:00:00',
                    'daytime_ends': '20:00:00',
                },
            },
            200,
            {
                'tariff_id': 'new_tariff_id',
                'tariff_type': 'support-taxi',
                'start_date': datetime.date(2021, 5, 1),
                'stop_date': datetime.date(9999, 12, 31),
                'cost_conditions': (
                    '{"rules": [{"cost_by_line": {"some_line": "456.78"}}]}'
                ),
                'benefit_conditions': (
                    '{"__default__": {"benefits": "654.32"}}'
                ),
                'countries': ['rus', 'blr'],
                'calc_night': True,
                'calc_holidays': True,
                'calc_workshifts': True,
                'daytime_begins': datetime.time(8, 0),
                'daytime_ends': datetime.time(20, 0),
            },
            datetime.date(2021, 5, 1),
        ),
        (
            'support-taxi',
            {
                'tariff': {
                    'tariff_id': 'new_tariff_id',
                    'start_date': '2021-05-01',
                    'cost_conditions': {
                        'rules': [{'cost_by_line': {'some_line': '456.78'}}],
                    },
                    'benefit_conditions': {
                        '__default__': {'benefits': '654.32'},
                    },
                    'countries': ['blr'],
                    'calc_night': True,
                    'calc_holidays': True,
                    'calc_workshifts': True,
                    'daytime_begins': '08:00:00',
                    'daytime_ends': '20:00:00',
                },
            },
            200,
            {
                'tariff_id': 'new_tariff_id',
                'tariff_type': 'support-taxi',
                'start_date': datetime.date(2021, 5, 1),
                'stop_date': datetime.date(9999, 12, 31),
                'cost_conditions': (
                    '{"rules": [{"cost_by_line": {"some_line": "456.78"}}]}'
                ),
                'benefit_conditions': (
                    '{"__default__": {"benefits": "654.32"}}'
                ),
                'countries': ['blr'],
                'calc_night': True,
                'calc_holidays': True,
                'calc_workshifts': True,
                'daytime_begins': datetime.time(8, 0),
                'daytime_ends': datetime.time(20, 0),
            },
            None,
        ),
    ],
)
async def test_apply(
        web_context,
        web_app_client,
        tariff_type,
        data,
        expected_status,
        expected_pg_result,
        expected_old_tariff_stop_date,
):
    response = await web_app_client.post(
        '/v1/tariffs/{}/apply'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT tariff_id, tariff_type, start_date, stop_date,'
            'cost_conditions, benefit_conditions, countries, calc_night, '
            'calc_holidays, calc_workshifts, daytime_begins, daytime_ends '
            'FROM piecework.tariff WHERE tariff_id = $1',
            data['tariff']['tariff_id'],
        )
        old_tariff_stop_date = await conn.fetchval(
            'SELECT stop_date FROM piecework.tariff WHERE tariff_id = $1',
            'current_tariff_id',
        )

    assert dict(pg_result) == expected_pg_result

    if expected_old_tariff_stop_date is not None:
        assert old_tariff_stop_date == pg_result['start_date']


@pytest.mark.parametrize(
    ['data', 'expected_response'],
    [
        (
            {},
            {
                'tariffs': [
                    {
                        'tariff_type': 'support-taxi',
                        'start_date': '2021-01-01',
                        'stop_date': '9999-12-31',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'active': True,
                        'tariff_id': 'current_tariff_id',
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                ],
            },
        ),
        (
            {'active': True},
            {
                'tariffs': [
                    {
                        'tariff_type': 'support-taxi',
                        'start_date': '2021-01-01',
                        'stop_date': '9999-12-31',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'active': True,
                        'tariff_id': 'current_tariff_id',
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                ],
            },
        ),
        ({'active': True, 'active_date': '2020-12-31'}, {'tariffs': []}),
        (
            {'tariff_type': 'support-taxi'},
            {
                'tariffs': [
                    {
                        'tariff_type': 'support-taxi',
                        'start_date': '2021-01-01',
                        'stop_date': '9999-12-31',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'active': True,
                        'tariff_id': 'current_tariff_id',
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                ],
            },
        ),
        ({'tariff_type': 'call-taxi'}, {'tariffs': []}),
        (
            {'country': 'rus'},
            {
                'tariffs': [
                    {
                        'tariff_type': 'support-taxi',
                        'start_date': '2021-01-01',
                        'stop_date': '9999-12-31',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'active': True,
                        'tariff_id': 'current_tariff_id',
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                ],
            },
        ),
        (
            {'country': 'blr'},
            {
                'tariffs': [
                    {
                        'tariff_type': 'support-taxi',
                        'start_date': '2021-01-01',
                        'stop_date': '9999-12-31',
                        'countries': ['rus', 'blr'],
                        'calc_night': True,
                        'calc_holidays': True,
                        'calc_workshifts': True,
                        'active': True,
                        'tariff_id': 'current_tariff_id',
                        'daytime_begins': '07:30:00',
                        'daytime_ends': '21:30:00',
                    },
                ],
            },
        ),
        ({'country': 'mda'}, {'tariffs': []}),
        ({'older_than': 'current_tariff_id', 'limit': 1}, {'tariffs': []}),
    ],
)
async def test_tariffs_list(web_app_client, data, expected_response):
    response = await web_app_client.post('/v1/tariffs/list', json=data)
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    'tariff_id, expected_status',
    [
        # Missing tariff
        ('missing_tariff_id', 404),
        # All OK
        ('current_tariff_id', 200),
    ],
)
async def test_get_tariff(web_app_client, tariff_id, expected_status):
    response = await web_app_client.get(
        '/v1/tariff/support-taxi/{}'.format(tariff_id),
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    response_data = await response.json()
    assert response_data == {
        'tariff': {
            'start_date': '2021-01-01',
            'stop_date': '9999-12-31',
            'active': True,
            'cost_conditions': {
                'rules': [{'cost_by_line': {'some_line': '123.45'}}],
            },
            'benefit_conditions': {'__default__': {'benefits': '321.00'}},
            'countries': ['rus', 'blr'],
            'calc_night': True,
            'calc_holidays': True,
            'calc_workshifts': True,
            'tariff_id': 'current_tariff_id',
            'tariff_type': 'support-taxi',
            'daytime_begins': '07:30:00',
            'daytime_ends': '21:30:00',
        },
    }
