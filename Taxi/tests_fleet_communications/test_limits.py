import pytest

AUTH_HEADERS = {
    'X-Yandex-UID': str(998),
    'X-Ya-User-Ticket': 'TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': 'PARK-01',
    'X-Idempotency-Token': 'TOKEN-01',
}

AUTH_HEADERS_400 = {
    'X-Yandex-UID': str(998),
    'X-Ya-User-Ticket': 'TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': 'PARK-400',
    'X-Idempotency-Token': 'TOKEN-01',
}

FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS = {
    'parks': [
        {
            'id': 'PARK-01',
            'restrictions': {
                'is_enabled_messages': True,
                'limits': {
                    'max_persons': 500,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                    'time_limits': {
                        'hour': 5,
                        'day': 100,
                        'week': 500,
                        'month': 1500,
                    },
                },
            },
        },
    ],
    'subscriptions': [
        {
            'id': 'premium',
            'restrictions': {
                'is_enabled_messages': True,
                'limits': {
                    'max_persons': 600,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                },
            },
        },
        {
            'id': 'base',
            'restrictions': {
                'is_enabled_messages': True,
                'limits': {
                    'max_title_length': 100,
                    'max_message_length': 1000,
                    'time_limits': {
                        'hour': 1,
                        'day': 20,
                        'week': 100,
                        'month': 400,
                    },
                },
            },
        },
    ],
    'default': {
        'restrictions': {
            'is_enabled_messages': False,
            'limits': {'max_title_length': 100, 'max_message_length': 1000},
        },
    },
}


def make_restriction(hour=None, day=None, week=None, month=None):
    config = {
        'is_enabled_messages': True,
        'limits': {
            'max_message_length': 1000,
            'max_title_length': 100,
            'max_persons': 500,
        },
    }
    if hour or day or week or month:
        config['limits']['time_limits'] = {}
    if hour:
        config['limits']['time_limits']['hour'] = hour
    if day:
        config['limits']['time_limits']['day'] = day
    if week:
        config['limits']['time_limits']['week'] = week
    if month:
        config['limits']['time_limits']['month'] = month
    return config


def make_response(status, available_at, day, week, month, hour=None):
    response = {
        'status': status,
        'available_at': available_at,
        'restriction': {
            'is_enabled': True,
            'max_person': 500,
            'max_title_length': 100,
            'max_message_length': 1000,
            'time_limit': {'day': day, 'week': week, 'month': month},
        },
    }
    if hour:
        response['restriction']['time_limit']['hour'] = hour
    return response


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_limits_get_empty_config(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings/limits', headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'restriction': {
            'is_enabled': True,
            'max_title_length': 120,
            'max_message_length': 512,
        },
        'status': 'ok',
    }


@pytest.mark.config(
    FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS=FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS,  # noqa: E501
)
@pytest.mark.parametrize(
    'park_id, mock_response',
    [
        (
            'PARK-01',
            {
                'status': 'ok',
                'restriction': {
                    'is_enabled': True,
                    'max_person': 500,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                    'time_limit': {
                        'hour': 5,
                        'day': 100,
                        'week': 500,
                        'month': 1500,
                    },
                },
            },
        ),
        (
            'PARK-02',
            {
                'status': 'ok',
                'restriction': {
                    'is_enabled': True,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                    'time_limit': {
                        'hour': 1,
                        'day': 20,
                        'week': 100,
                        'month': 400,
                    },
                },
            },
        ),
        (
            'PARK-03',
            {
                'status': 'mailing_not_enable',
                'restriction': {
                    'is_enabled': False,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                },
            },
        ),
        (
            'PARK-04',
            {
                'status': 'ok',
                'restriction': {
                    'is_enabled': True,
                    'max_person': 600,
                    'max_title_length': 100,
                    'max_message_length': 1000,
                },
            },
        ),
    ],
)
@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_limits_get_limit_choosen(
        mock_api, pg_dump, taxi_fleet_communications, park_id, mock_response,
):
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings/limits',
        headers={
            'X-Yandex-UID': str(998),
            'X-Ya-User-Ticket': 'TICKET',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Park-Id': park_id,
            'X-Idempotency-Token': 'TOKEN-01',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == mock_response


@pytest.mark.parametrize(
    'status, available_at, hour, day, week, month',
    [
        pytest.param(
            'hour',
            '2022-01-01T15:01:00+00:00',
            1,
            100,
            500,
            1500,
            marks=[pytest.mark.now('2022-01-01T14:30:00+00:00')],
        ),
        pytest.param(
            'day',
            '2022-01-02T13:11:00+00:00',
            None,
            2,
            500,
            1500,
            marks=[pytest.mark.now('2022-01-02T13:00:00+00:00')],
        ),
        pytest.param(
            'week',
            '2022-01-08T12:01:00+00:00',
            None,
            4,
            3,
            1500,
            marks=[pytest.mark.now('2022-01-08T11:00:00+00:00')],
        ),
        pytest.param(
            'month',
            '2022-01-31T12:01:00+00:00',
            None,
            10,
            20,
            3,
            marks=[pytest.mark.now('2022-01-31T11:00:00+00:00')],
        ),
    ],
)
async def test_mailing_limits_get_limit_bounds(
        mock_api,
        pg_dump,
        taxi_fleet_communications,
        taxi_config,
        status,
        available_at,
        hour,
        day,
        week,
        month,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': {
                'parks': [
                    {
                        'id': 'PARK-01',
                        'restrictions': make_restriction(
                            hour=hour, day=day, week=week, month=month,
                        ),
                    },
                ],
                'subscriptions': [],
                'default': {'restrictions': make_restriction()},
            },
        },
    )
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings/limits',
        headers={
            'X-Yandex-UID': str(998),
            'X-Ya-User-Ticket': 'TICKET',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Park-Id': 'PARK-01',
            'X-Idempotency-Token': 'TOKEN-01',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == make_response(
        status=status,
        available_at=available_at,
        hour=hour,
        day=day,
        week=week,
        month=month,
    )


@pytest.mark.pgsql('fleet_communications', files=['pg_add_mailings.sql'])
@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_limit_deleted_msg(
        mock_api, pg_dump, taxi_fleet_communications, taxi_config,
):

    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': {
                'parks': [
                    {
                        'id': 'PARK-01',
                        'restrictions': make_restriction(hour=1),
                    },
                ],
                'subscriptions': [],
                'default': {'restrictions': make_restriction()},
            },
        },
    )
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings/limits', headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'restriction': {
            'is_enabled': True,
            'max_title_length': 100,
            'max_message_length': 1000,
            'max_person': 500,
            'time_limit': {'hour': 1},
        },
        'status': 'hour',
        'available_at': '2022-01-02T13:01:00+00:00',
    }
