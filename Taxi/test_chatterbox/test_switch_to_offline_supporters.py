# pylint: disable=no-member
import datetime

import pytest
import pytz

from taxi import discovery

from chatterbox.crontasks import switch_to_offline_inactive_supporters
from chatterbox.crontasks import switch_to_offline_offer_skipped_supporters

NOW = datetime.datetime(2019, 8, 13, 12, 0, 0)


@pytest.mark.parametrize(
    'expected_db, expected_request_data, expected_skip_offer_count_clear',
    [
        (
            [
                (
                    'user_1',
                    'offline',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(2019, 8, 13, 12, 0, 0, tzinfo=pytz.utc),
                ),
                (
                    'user_10',
                    'online',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_2',
                    'offline',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(2019, 8, 13, 12, 0, 0, tzinfo=pytz.utc),
                ),
                (
                    'user_3',
                    'online',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_4',
                    'online',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_5',
                    'offline',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_6',
                    'offline',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_7',
                    'offline',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_8',
                    'offline',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_9',
                    'online',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
            ],
            {
                'events': [
                    {
                        'id': (
                            'supporter_status'
                            '_172beea4aff3e55d565b6a08e14689ee3bd2f03a'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'online',
                            'login': 'user_2',
                            'lines': ['first', 'new'],
                            'projects': ['eats', 'taxi'],
                            'in_addition': True,
                            'start_timestamp': '2019-08-13T14:49:25+0300',
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                        },
                    },
                    {
                        'id': (
                            'supporter_status'
                            '_f7ae5ee66d8a5907c6fc9a9e2e2d215ea4adfe7e'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'online',
                            'login': 'user_1',
                            'in_addition': False,
                            'lines': ['first'],
                            'projects': ['eats'],
                            'start_timestamp': '2019-08-13T14:49:25+0300',
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                        },
                    },
                ],
            },
            ['user_1', 'user_2'],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={'first': {'projects': ['eats']}, 'new': {}},
)
async def test_switch_to_offline(
        cbox_context,
        loop,
        expected_db,
        expected_request_data,
        expected_skip_offer_count_clear,
        patch_aiohttp_session,
        response_mock,
):

    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: (d['created'], d['id']),
        )
        for event in kwargs['json']['events']:
            event['payload']['projects'] = sorted(event['payload']['projects'])
        assert kwargs['json'] == expected_request_data
        return response_mock(json={})

    await switch_to_offline_inactive_supporters.do_stuff(cbox_context, loop)

    async with cbox_context.data.pg_master_pool.acquire() as conn:
        supporters = await conn.fetch(
            'SELECT * from chatterbox.online_supporters '
            'ORDER BY supporter_login',
        )
    for i, record in enumerate(supporters):
        assert record == expected_db[i]

    async with cbox_context.data.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = ANY($1)',
            expected_skip_offer_count_clear,
        )
    for item in result:
        assert item['offer_skip_count'] == 0


@pytest.mark.parametrize(
    'expected_db, expected_request_data, expected_skip_offer_count_clear',
    [
        (
            [
                (
                    'user_1',
                    'online',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_10',
                    'offline',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(2019, 8, 13, 12, 0, 0, tzinfo=pytz.utc),
                ),
                (
                    'user_2',
                    'offline',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(2019, 8, 13, 12, 0, 0, tzinfo=pytz.utc),
                ),
                (
                    'user_3',
                    'online',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_4',
                    'online',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_5',
                    'offline',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_6',
                    'offline',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_7',
                    'offline',
                    ['first'],
                    True,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_8',
                    'offline',
                    ['first'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
                (
                    'user_9',
                    'online',
                    ['first', 'new'],
                    False,
                    datetime.datetime(
                        2019, 8, 13, 11, 51, 25, tzinfo=pytz.utc,
                    ),
                    datetime.datetime(
                        2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc,
                    ),
                ),
            ],
            {
                'events': [
                    {
                        'created': '2019-08-13T15:00:00+0300',
                        'id': (
                            'supporter_status'
                            '_172beea4aff3e55d565b6a08e14689ee3bd2f03a'
                        ),
                        'payload': {
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                            'in_addition': True,
                            'lines': ['first', 'new'],
                            'login': 'user_2',
                            'projects': ['eats', 'taxi'],
                            'start_timestamp': '2019-08-13T14:49:25+0300',
                            'status': 'online',
                        },
                        'type': 'supporter_status',
                    },
                    {
                        'id': (
                            'supporter_status'
                            '_53691118e92599eb10be31c03ec66ed50cb4eb60'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                            'in_addition': False,
                            'lines': ['first', 'new'],
                            'login': 'user_10',
                            'projects': ['eats', 'taxi'],
                            'start_timestamp': '2019-08-13T14:49:25+0300',
                            'status': 'online',
                        },
                    },
                ],
            },
            ['user_2', 'user_10'],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={'first': {'projects': ['eats']}, 'new': {}},
    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={
        '__default__': 1000,
        'first': 5,
        'new': 6,
    },
)
async def test_switch_to_offline_skip_offer_skipped(
        cbox_context,
        loop,
        expected_db,
        expected_request_data,
        expected_skip_offer_count_clear,
        patch_aiohttp_session,
        response_mock,
):

    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: (d['created'], d['id']),
        )
        for event in kwargs['json']['events']:
            event['payload']['projects'] = sorted(event['payload']['projects'])
        assert kwargs['json'] == expected_request_data
        return response_mock(json={})

    await switch_to_offline_offer_skipped_supporters.do_stuff(
        cbox_context, loop,
    )

    async with cbox_context.data.pg_master_pool.acquire() as conn:
        supporters = await conn.fetch(
            'SELECT * from chatterbox.online_supporters '
            'ORDER BY supporter_login',
        )
    for i, record in enumerate(supporters):
        assert record == expected_db[i]

    async with cbox_context.data.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = ANY($1)',
            expected_skip_offer_count_clear,
        )
    for item in result:
        assert item['offer_skip_count'] == 0
