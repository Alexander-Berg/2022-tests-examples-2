import datetime

import pytest
import pytz

TASK_NAME = 'configs_changing'

TIMEZONE = pytz.timezone('Europe/Moscow')
UTCNOW_STR = '2021-04-12T10:00:19Z'
UTCNOW = datetime.datetime.strptime(UTCNOW_STR, '%Y-%m-%dT%H:%M:%SZ')
NOW = TIMEZONE.fromutc(UTCNOW)

MESSAGE = [
    '<b>Group:</b> #efficiency',
    '⚙<b> Config </b> <a href=\'https://tariff-editor.taxi.yandex-team.ru'
    '/dev/configs/edit/DISPATCH_BUFFER_SETTINGS\'>DISPATCH_BUFFER_SETTINGS</a>'
    ' was changed by user <a href=\'https://staff.yandex-team.ru/dlefimov\'>'
    'dlefimov</a> and approved by '
    '<a href=\'https://staff.yandex-team.ru/dlefimov\'>dlefimov</a>',
    '<code>$insert:',
    '  timeout: 50',
    'enabled:',
    '- false',
    '- true',
    '</code>',
    f'[{(NOW - datetime.timedelta(seconds=5))}]',
    '<b>owners:</b> @tsarkov',
    'subscribers: @dlefimov',
]
MESSAGE_WITHOUT_LOGINS = [
    '<b>Group:</b> #efficiency',
    '⚙<b> Config </b> <a href=\'https://tariff-editor.taxi.yandex-team.ru'
    '/dev/configs/edit/DISPATCH_BUFFER_SETTINGS\'>DISPATCH_BUFFER_SETTINGS</a>'
    ' was changed by user <a href=\'https://staff.yandex-team.ru/dlefimov\'>'
    'dlefimov</a> and approved by '
    '<a href=\'https://staff.yandex-team.ru/dlefimov\'>dlefimov</a>',
    '<code>$insert:',
    '  timeout: 50',
    'enabled:',
    '- false',
    '- true',
    '</code>',
    f'[{(NOW - datetime.timedelta(seconds=5))}]',
    '<b>owners:</b> (Can\'t get logins)',
]
YANFORMATOR_BOT_SETTINGS = {
    'task_retry_count': 1,
    'task_delay': 10,
    'max_summary_length': 100,
    'max_notify_length': 4000,
}


@pytest.mark.now(UTCNOW_STR)
@pytest.mark.parametrize(
    'from_timestamp,check_delay,messages_count,message,is_staff_failed',
    [
        # utc
        (None, 0, None, None, False),
        (UTCNOW - datetime.timedelta(seconds=10), 0, 1, MESSAGE, False),
        (
            UTCNOW - datetime.timedelta(seconds=10),
            0,
            1,
            MESSAGE_WITHOUT_LOGINS,
            True,
        ),
        (UTCNOW - datetime.timedelta(seconds=10), 10, 0, MESSAGE, False),
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
            'configs': {
                'patterns': [r'DISPATCH_BUFFER.*'],
                'names': ['SURGER_SETTINGS'],
                'names_exclude': ['AIRPORT_SETTINGS'],
            },
        },
        {
            'info': {'name': 'efficiency1', 'telegram_channels': []},
            'configs': {'patterns': [r'NOT_DISPATCH_BUFFER.*']},
        },
        {
            'info': {'name': 'efficiency2', 'telegram_channels': []},
            'configs': {'names': ['SURGER_SETTINGS']},
        },
        {'info': {'name': 'infrastructure', 'telegram_channels': []}},
    ],
)
async def test_configs(
        mockserver,
        testpoint,
        stq_runner,
        taxi_config,
        redis_store,
        from_timestamp,
        check_delay,
        messages_count,
        message,
        is_staff_failed,
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
        return [
            {
                'id': '606adc7c1eeaed2605bfba53',
                'login': 'dlefimov',
                'arguments': {
                    'response': {
                        'created_by': 'dlefimov',
                        'service_name': 'configs-admin',
                        'summary': {
                            'new': {
                                'enabled': True,
                                'limit': 100,
                                'timeout': 50,
                            },
                            'current': {'enabled': False, 'limit': 100},
                        },
                        'query_params': {'name': 'DISPATCH_BUFFER_SETTINGS'},
                    },
                },
                'timestamp': (NOW - datetime.timedelta(seconds=5)).strftime(
                    '%Y-%m-%dT%H:%M:%S.%f%z',
                ),
            },
        ]

    @mockserver.json_handler('staff/v3/persons')
    def _persons(_):
        if is_staff_failed:
            return mockserver.make_response(status=500)
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
            'task:configs_changing',
            'update_from',
            from_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        )

    YANFORMATOR_BOT_SETTINGS['check_delay'] = check_delay
    taxi_config.set_values(
        {'YANFORMATOR_BOT_SETTINGS': YANFORMATOR_BOT_SETTINGS},
    )

    await stq_runner.yanformator_bot_configs_changing.call(
        task_id=TASK_NAME, args=[],
    )

    if messages_count is None:
        await _update_from_created.wait_call()
    else:
        messages = (await _get_messages.wait_call())['data']

        assert len(messages) == messages_count
        if messages_count:
            assert message == [
                el for el in messages[0].split('\n') if el != ''
            ]

    assert (
        redis_store.hget('task:configs_changing', 'update_from').decode()
        == UTCNOW_STR
    )


@pytest.mark.now(UTCNOW_STR)
@pytest.mark.parametrize(
    'from_timestamp,check_delay,messages_count,message,is_staff_failed',
    [(UTCNOW - datetime.timedelta(seconds=10), 10, 0, MESSAGE, False)],
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
            'configs': {
                'patterns': [],
                'names': [],
                'names_exclude': [],
                'groups': ['DISPATCH_BUFFER'],
            },
        },
    ],
)
async def test_configs_groups(
        mockserver,
        testpoint,
        stq_runner,
        taxi_config,
        redis_store,
        from_timestamp,
        check_delay,
        messages_count,
        message,
        is_staff_failed,
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
        return [
            {
                'id': '606adc7c1eeaed2605bfba53',
                'login': 'dlefimov',
                'arguments': {
                    'response': {
                        'created_by': 'dlefimov',
                        'service_name': 'configs-admin',
                        'summary': {
                            'new': {
                                'enabled': True,
                                'limit': 100,
                                'timeout': 50,
                            },
                            'current': {'enabled': False, 'limit': 100},
                        },
                        'query_params': {'name': 'DISPATCH_BUFFER_SETTINGS'},
                    },
                },
                'timestamp': (NOW - datetime.timedelta(seconds=5)).strftime(
                    '%Y-%m-%dT%H:%M:%S.%f%z',
                ),
            },
        ]

    @mockserver.json_handler('staff/v3/persons')
    def _persons(_):
        if is_staff_failed:
            return mockserver.make_response(status=500)
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
            'task:configs_changing',
            'update_from',
            from_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        )

    YANFORMATOR_BOT_SETTINGS['check_delay'] = check_delay
    taxi_config.set_values(
        {'YANFORMATOR_BOT_SETTINGS': YANFORMATOR_BOT_SETTINGS},
    )

    await stq_runner.yanformator_bot_configs_changing.call(
        task_id=TASK_NAME, args=[],
    )

    if messages_count is None:
        await _update_from_created.wait_call()
    else:
        messages = (await _get_messages.wait_call())['data']

        assert len(messages) == messages_count
        if messages_count:
            assert message == [
                el for el in messages[0].split('\n') if el != ''
            ]

    assert (
        redis_store.hget('task:configs_changing', 'update_from').decode()
        == UTCNOW_STR
    )
