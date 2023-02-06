import uuid

import pytest

ENDPOINT = '/internal/fleet-notifications-telegram-bot/v1/message'

MESSAGE = {'text': 'MessageBlaBlaBlaBla'}


def _get_last_message_id(pgsql, receiver):
    db = pgsql['fleet_notifications_telegram_bot'].cursor()
    db.execute(
        'SELECT last_message_id '
        'FROM fleet_notifications_telegram_bot.tg_users_info '
        f'WHERE receiver = {receiver}::PARK_USER_PAIR',
    )
    return list(db)[0][0]


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'receivers, pd_ids,',
    [
        pytest.param(
            [{'park_id': 'p1', 'user_id': '1'}],
            ['pd1'],
            id='send_one_message',
        ),
        pytest.param(
            [
                {'park_id': 'p1', 'user_id': '1'},
                {'park_id': 'p1', 'user_id': '2'},
            ],
            ['pd1', 'pd2'],
            id='send_a_few messages',
        ),
        pytest.param(
            [
                {'park_id': 'p1', 'user_id': '1'},
                {'park_id': 'p1', 'user_id': '3'},
            ],
            ['pd1'],
            id='send_message_when_same_pd_id',
        ),
    ],
)
async def test_ok(
        taxi_fleet_notifications_telegram_bot_web, stq, receivers, pd_ids,
):
    x_idempotency_token = str(uuid.uuid4())
    headers = {'X-Idempotency-Token': x_idempotency_token}

    json_request = {'receivers': receivers, 'message': MESSAGE}

    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers, json=json_request,
    )

    assert response.status == 200

    assert (
        stq.fleet_notifications_telegram_bot_send_message.times_called
        == len(pd_ids)
    )
    for pd_id in pd_ids:
        stq_args = (
            stq.fleet_notifications_telegram_bot_send_message.next_call()
        )
        assert (
            stq_args['queue']
            == 'fleet_notifications_telegram_bot_send_message'
        )
        assert stq_args['id'] == f'{x_idempotency_token}_{pd_id}'
        assert stq_args['args'][0] == pd_id
        assert stq_args['args'][1] == MESSAGE['text']


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.config(
    FLEET_NOTIFICATIONS_TELEGRAM_BOT_MESSAGE_SETTINGS_V2={
        'max_message_to_send_len': 20,
        'stq_amount_in_one_builder': 1,
    },
)
@pytest.mark.parametrize(
    'receivers, message, expected_code',
    [
        pytest.param(
            [{'park_id': 'p1', 'user_id': '1'}],
            {'text': MESSAGE['text'] + MESSAGE['text']},
            400,
            id='message too long',
        ),
    ],
)
async def test_not_ok(
        taxi_fleet_notifications_telegram_bot_web,
        stq,
        receivers,
        message,
        expected_code,
):
    x_idempotency_token = str(uuid.uuid4())
    headers = {'X-Idempotency-Token': x_idempotency_token}

    json_request = {'receivers': receivers, 'message': message}

    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers, json=json_request,
    )

    assert response.status == expected_code


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'receivers, idemp_token, stq_times_called',
    [
        pytest.param(
            [{'park_id': 'p1', 'user_id': '1'}],
            'it1111111111111111111111',
            1,
            id='send twice',
        ),
        pytest.param(
            [{'park_id': 'p1', 'user_id': '1'}],
            'it2222222222222222222222',
            0,
            id='send existing',
        ),
    ],
)
async def test_check_idemp(
        taxi_fleet_notifications_telegram_bot_web,
        stq,
        pgsql,
        receivers,
        idemp_token,
        stq_times_called,
):
    headers = {'X-Idempotency-Token': idemp_token}

    json_request = {'receivers': receivers, 'message': MESSAGE}

    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers, json=json_request,
    )
    assert response.status == 200
    assert (
        _get_last_message_id(
            pgsql, (receivers[0]['park_id'], receivers[0]['user_id']),
        )
        == idemp_token
    )
    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers, json=json_request,
    )
    assert response.status == 200
    assert (
        stq.fleet_notifications_telegram_bot_send_message.times_called
        == stq_times_called
    )
