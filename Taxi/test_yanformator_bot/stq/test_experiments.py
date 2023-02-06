# pylint: disable=pointless-string-statement

import datetime
import re

import pytest
import pytz

TASK_NAME = 'experiments_changing'

TIMEZONE = pytz.timezone('Europe/Moscow')
UTCNOW_STR = '2021-04-12T10:00:19Z'
UTCNOW = datetime.datetime.strptime(UTCNOW_STR, '%Y-%m-%dT%H:%M:%SZ')
NOW = TIMEZONE.fromutc(UTCNOW)

YANFORMATOR_BOT_SETTINGS = {
    'task_retry_count': 1,
    'task_delay': 10,
    'max_summary_length': 100,
    'max_notify_length': 4000,
}


@pytest.mark.now(UTCNOW_STR)
@pytest.mark.parametrize(
    'from_timestamp,check_delay,messages_count',
    [
        # utc
        (None, 0, None),
        (UTCNOW - datetime.timedelta(seconds=10), 0, 3),
        (UTCNOW - datetime.timedelta(seconds=10), 10, 0),
    ],
)
@pytest.mark.config(
    YANFORMATOR_BOT_NOTIFICATION_SETTINGS=[
        {
            'info': {
                'name': 'efficiency',
                'owners': ['alex-tsarkov'],
                'telegram_channels': [],
                'subscribers': ['dlefimov'],
            },
            'experiments': {
                'patterns': [r'coord_control.*'],
                'names': ['surge_exp'],
                'names_exclude': ['airport_exp'],
            },
        },
        {
            'info': {'name': 'efficiency1', 'telegram_channels': []},
            'experiments': {'patterns': [r'not_coord_control.*']},
        },
        {
            'info': {
                'name': 'efficiency',
                'owners': ['alex-tsarkov'],
                'telegram_channels': [],
                'subscribers': ['dlefimov'],
            },
            'experiments': {'names': ['dispatch_buffer_test']},
        },
        {'info': {'name': 'infrastructure', 'telegram_channels': []}},
    ],
)
async def test_experiments(
        mockserver,
        testpoint,
        load_json,
        stq_runner,
        taxi_config,
        redis_store,
        from_timestamp,
        check_delay,
        messages_count,
):
    @testpoint('messages')
    async def _get_messages(data):
        return data

    @testpoint('update_from_created')
    async def _update_from_created(data):
        return data

    @mockserver.json_handler('audit/v1/client/logs/retrieve/')
    def _client_logs(request):
        update_from = (
            datetime.datetime.strptime(
                request.json['query']['date_from'], '%Y-%m-%dT%H:%M:%S%z',
            )
            .astimezone(tz=datetime.timezone.utc)
            .replace(tzinfo=None)
        )
        if update_from >= UTCNOW:
            return []
        """
        curl --location --request
        POST 'audit.taxi.tst.yandex.net/v1/client/logs/retrieve'
        --header 'X-Ya-Service-Ticket: '<Ticket>'
        --header 'Content-Type: application/json' --data-raw
        '{
            "query": {
                "actions": [
                    "put_approval"
                ],
                "date_from": "2021-05-16T18:00:00Z"
            }
        }'
        """
        responses = load_json('audit_response.json')
        for response in responses:
            response['timestamp'] = (
                NOW - datetime.timedelta(seconds=5)
            ).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        return responses

    @mockserver.json_handler('staff/v3/persons')
    def _persons(_):
        return {
            'result': [
                {
                    'login': 'alex-tsarkov',
                    'accounts': [{'type': 'telegram', 'value': 'tsarkov'}],
                },
                {
                    'login': 'dlefimov',
                    'accounts': [{'type': 'telegram', 'value': 'dlefimov'}],
                },
            ],
        }

    if from_timestamp:
        redis_store.hset(
            'task:experiments_changing',
            'update_from',
            from_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        )

    YANFORMATOR_BOT_SETTINGS['check_delay'] = check_delay
    taxi_config.set_values(
        {'YANFORMATOR_BOT_SETTINGS': YANFORMATOR_BOT_SETTINGS},
    )

    await stq_runner.yanformator_bot_experiments_changing.call(
        task_id=TASK_NAME, args=[],
    )

    if messages_count is None:
        await _update_from_created.wait_call()
    else:
        messages = (await _get_messages.wait_call())['data']

        assert len(messages) == messages_count
        if messages_count:

            def transform(message):
                return re.sub(r'<code>([\S\s]*)</code>', '', message)

            assert sorted(map(transform, messages)) == sorted(
                map(transform, load_json('messages.json')),
            )

    assert (
        redis_store.hget('task:experiments_changing', 'update_from').decode()
        == UTCNOW_STR
    )
