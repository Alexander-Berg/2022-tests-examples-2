# pylint: disable=C5521, W0621
import datetime
from typing import Optional

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools
from tests_tags.tags.yql_services_fixture import (  # noqa: F401
    local_yql_services,
)


_NOW = datetime.datetime.now()
_BEFORE = _NOW - datetime.timedelta(hours=1)
_AFTER = _NOW + datetime.timedelta(hours=1)

_BASE = datetime.datetime(2021, 3, 23, 13, 0, 0, tzinfo=None)
_BASE_MINUS_1_DAY = _BASE - datetime.timedelta(days=1)
_BASE_MINUS_2_DAYS = _BASE - datetime.timedelta(days=2)
_BASE_MINUS_2_DAYS_1_MINUTE = _BASE - datetime.timedelta(days=2, minutes=1)
_BASE_MINUS_2_DAYS_PLUS_1_MINUTE = _BASE_MINUS_2_DAYS + datetime.timedelta(
    minutes=1,
)
_BASE_MINUS_3_DAYS = _BASE - datetime.timedelta(days=3)
_BASE_MINUS_2_HOURS = _BASE - datetime.timedelta(hours=2)
_BASE_MINUS_2_HOURS_1_MINUTE = _BASE - datetime.timedelta(hours=2, minutes=1)
_BASE_MINUS_10_MINUTES = _BASE - datetime.timedelta(minutes=10)
_BASE_MINUS_11_MINUTES = _BASE - datetime.timedelta(minutes=11)

_NO_EMAIL = None

_EXPIRATION_EMAIL_XML = (
    '<?xml version="1.0"?><mails><mail>'
    '<from>yandex-taxi-tags service &lt;no-reply@yandex-team.ru&gt;'
    '</from><subject>YQL query was disabled</subject>'
    '<body>YQL query "query 0" is disabled due to reaching expiration date.\n'
    'https://tariff-editor.taxi.yandex-team.ru/tag-queries/tags/edit/'
    'query%200/information\n'
    '</body></mail></mails>'
)

_UPCOMING_EXPIRATION_EMAIL_XML = (
    '<?xml version="1.0"?><mails><mail>'
    '<from>yandex-taxi-tags service &lt;no-reply@yandex-team.ru&gt;'
    '</from><subject>YQL query is going to expire soon</subject>'
    '<body>YQL query "query 0" expires soon and will be disabled at '
    '2021-03-23T13:00:00+0000 (in 23.03.2021 at 16:00 MSK).\n'
    'https://tariff-editor.taxi.yandex-team.ru/tag-queries/tags/edit/'
    'query%200/information\n'
    'Consider agreement on new TTL.\n'
    '</body></mail></mails>'
)


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider.from_id(index) for index in range(6)],
        ),
        yql_tools.insert_operation(
            operation_id='operation_id_3',
            provider_id=3,
            entity_type=None,
            status='running',
            started=_BEFORE.isoformat(),
        ),
        yql_tools.insert_operation(
            operation_id='operation_id_4',
            provider_id=4,
            entity_type=None,
            status='completed',
            started=_BEFORE.isoformat(),
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='disabled_query',
                    provider_id=0,
                    tags=['tag0', 'tags1'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=False,
                ),
                yql_tools.Query(
                    name='disabled_and_expired_query',
                    provider_id=1,
                    tags=['tag0', 'tags1'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=False,
                    disable_at=_BEFORE,
                ),
                yql_tools.Query(
                    name='query_without_disable_at',
                    provider_id=2,
                    tags=['tag0'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=True,
                ),
                yql_tools.Query(
                    name='expired_query',
                    provider_id=3,
                    tags=['tags1', 'tag2'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=True,
                    disable_at=_BEFORE,
                ),
                yql_tools.Query(
                    name='now_expired_query',
                    provider_id=4,
                    tags=['tags2'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=True,
                    disable_at=_NOW,
                ),
                yql_tools.Query(
                    name='non_expired_query',
                    provider_id=5,
                    tags=['tags0', 'tags1', 'tags2'],
                    changed=_BEFORE.isoformat(),
                    created=_BEFORE.isoformat(),
                    enabled=True,
                    disable_at=_AFTER,
                ),
            ],
        ),
    ],
)
async def test_yql_disposer_basic(
        taxi_tags, local_yql_services, pgsql,  # noqa: F811
):
    local_yql_services.set_operation_id('operation_id_3')

    await tags_tools.activate_task(taxi_tags, 'yql-disposer')

    # check service.queries table
    queries = tags_select.select_table_named(
        'service.queries', 'provider_id', pgsql['tags'],
    )
    queries_enabled_info = [
        {'name': query['name'], 'enabled': query['enabled']}
        for query in queries
    ]
    assert queries_enabled_info == [
        {'name': 'disabled_query', 'enabled': False},
        {'name': 'disabled_and_expired_query', 'enabled': False},
        {'name': 'query_without_disable_at', 'enabled': True},
        {'name': 'expired_query', 'enabled': False},  # changed
        {'name': 'now_expired_query', 'enabled': False},  # changed
        {'name': 'non_expired_query', 'enabled': True},
    ]

    # check state.providers
    providers = tags_select.select_table_named(
        'state.providers', 'id', pgsql['tags'],
    )
    providers_enabled_info = [
        {'id': provider['id'], 'active': provider['active']}
        for provider in providers
    ]
    assert providers_enabled_info == [
        {'id': 0, 'active': True},
        {'id': 1, 'active': True},
        {'id': 2, 'active': True},
        {'id': 3, 'active': False},  # changed
        {'id': 4, 'active': False},  # changed
        {'id': 5, 'active': True},
    ]

    # check service.yql_operations
    yql_operations = tags_select.select_table_named(
        'service.yql_operations', 'operation_id', pgsql['tags'],
    )
    yql_operations = [
        {
            'operation_id': yql_operation['operation_id'],
            'status': yql_operation['status'],
        }
        for yql_operation in yql_operations
    ]
    assert yql_operations == [
        {'operation_id': 'operation_id_3', 'status': 'aborted'},
        {'operation_id': 'operation_id_4', 'status': 'completed'},
    ]

    # check service.tags_update_queue
    tags_update_queue = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', pgsql['tags'],
    )
    assert tags_update_queue == [
        {
            'provider_id': 3,
            'action': 'remove',
            'last_processed_revision': 0,
            'process_upto_revision': 1,
        },
        {
            'provider_id': 4,
            'action': 'remove',
            'last_processed_revision': 0,
            'process_upto_revision': 1,
        },
    ]

    # check yql cancel request
    assert local_yql_services.times_called['action']


def _verify_last_notified_at(pgsql, expected_time: Optional[str]):
    rows = tags_select.select_named(
        'SELECT last_notified_at  as last_notified_at '
        'FROM service.queries WHERE provider_id = 0',
        pgsql['tags'],
    )
    assert len(rows) == 1

    saved_time = rows[0]['last_notified_at']
    saved_time = saved_time.replace(tzinfo=None) if saved_time else None

    if expected_time is None:
        assert saved_time is None
    else:
        assert saved_time == expected_time


def _set_last_notified_at(pgsql, last_notified_at: str):
    cursor = pgsql['tags'].cursor()
    cursor.execute(
        f'UPDATE service.queries SET last_notified_at = \'{last_notified_at}\''
        f'  WHERE provider_id = 0',
        pgsql['tags'],
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider.from_id(0), tags_tools.Provider.from_id(1)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query 0',
                    0,
                    ['tag'],
                    _BASE_MINUS_3_DAYS,
                    _BASE_MINUS_3_DAYS,
                    'query',
                    yql_processing_method='yt_merge',
                    disable_at=_BASE,
                ),
                yql_tools.Query(
                    'query1',
                    1,
                    ['tag'],
                    _NOW,
                    _NOW,
                    'query',
                    yql_processing_method='yt_merge',
                ),
            ],
        ),
        yql_tools.insert_subscriptions(
            [
                yql_tools.Subscription(
                    0,
                    login,
                    [yql_tools.SubscriptionType('query_expiration', 'email')],
                )
                for login in ['d-captain', 'loginef']
            ],
        ),
    ],
)
@pytest.mark.config(
    TAGS_YQL_NOTIFICATION_SETTINGS={
        'failure': {'is_enabled': True, 'auto_subscribe_query_author': True},
        'upcoming_query_expiration': {
            'is_enabled': True,
            'auto_subscribe_query_author': True,
            'notification_schedule': [
                # test sorting also
                {'remaining_minutes': 10},
                {'remaining_days': 1},
                {'remaining_days': 2},
                {'remaining_hours': 2},
            ],
        },
        'query_expiration': {
            'is_enabled': True,
            'auto_subscribe_query_author': True,
        },
    },
)
@pytest.mark.parametrize(
    'last_notified_at, expect_sticker_call, expected_last_notified_at,'
    'expected_email_xml',
    [
        pytest.param(
            _BASE_MINUS_2_HOURS,
            True,
            _BASE_MINUS_2_HOURS,  # do not save notification time on expiration
            _EXPIRATION_EMAIL_XML,
            id='expiration',
            marks=[pytest.mark.now(_BASE.isoformat())],
        ),
        pytest.param(
            None,
            False,
            None,
            _NO_EMAIL,
            id='days_schedule_too_early',
            marks=[pytest.mark.now(_BASE_MINUS_2_DAYS_1_MINUTE.isoformat())],
        ),
        pytest.param(
            None,
            True,
            _BASE_MINUS_2_DAYS,
            _UPCOMING_EXPIRATION_EMAIL_XML,
            id='days_schedule',
            marks=[pytest.mark.now(_BASE_MINUS_2_DAYS.isoformat())],
        ),
        pytest.param(
            None,
            True,
            _BASE_MINUS_2_DAYS_PLUS_1_MINUTE,
            _UPCOMING_EXPIRATION_EMAIL_XML,
            id='days_schedule_little_late',
            marks=[
                pytest.mark.now(_BASE_MINUS_2_DAYS_PLUS_1_MINUTE.isoformat()),
            ],
        ),
        pytest.param(
            _BASE_MINUS_2_DAYS,
            False,
            _BASE_MINUS_2_DAYS,
            _NO_EMAIL,
            id='evade_duplicating_notification',
            marks=[pytest.mark.now(_BASE_MINUS_2_DAYS.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_2_DAYS,
            False,
            _BASE_MINUS_2_DAYS,
            _NO_EMAIL,
            id='evade_duplicating_notification_minute_shift',
            marks=[
                pytest.mark.now(_BASE_MINUS_2_DAYS_PLUS_1_MINUTE.isoformat()),
            ],
        ),
        pytest.param(
            _BASE_MINUS_2_DAYS,
            True,
            _BASE_MINUS_10_MINUTES,
            _UPCOMING_EXPIRATION_EMAIL_XML,
            id='one_message_for_multiple_schedule_entries',
            marks=[pytest.mark.now(_BASE_MINUS_10_MINUTES.isoformat())],
        ),
        pytest.param(
            None,
            False,
            None,
            _NO_EMAIL,
            id='too_early',
            marks=[pytest.mark.now(_BASE_MINUS_3_DAYS.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_3_DAYS,
            False,
            _BASE_MINUS_3_DAYS,
            _NO_EMAIL,
            id='too_early_query_prolonged_after_notifications',
            marks=[pytest.mark.now(_BASE_MINUS_2_DAYS_1_MINUTE.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_1_DAY,
            True,
            _BASE_MINUS_2_HOURS,
            _UPCOMING_EXPIRATION_EMAIL_XML,
            id='hours_schedule',
            marks=[pytest.mark.now(_BASE_MINUS_2_HOURS.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_1_DAY,
            False,
            _BASE_MINUS_1_DAY,
            _NO_EMAIL,
            id='hours_schedule_early',
            marks=[pytest.mark.now(_BASE_MINUS_2_HOURS_1_MINUTE.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_2_HOURS,
            True,
            _BASE_MINUS_10_MINUTES,
            _UPCOMING_EXPIRATION_EMAIL_XML,
            id='minutes_schedule',
            marks=[pytest.mark.now(_BASE_MINUS_10_MINUTES.isoformat())],
        ),
        pytest.param(
            _BASE_MINUS_2_HOURS,
            False,
            _BASE_MINUS_2_HOURS,
            _NO_EMAIL,
            id='minutes_schedule_early',
            marks=[pytest.mark.now(_BASE_MINUS_11_MINUTES.isoformat())],
        ),
        pytest.param(
            None,
            False,
            None,
            _NO_EMAIL,
            id='expiration_disabled',
            marks=[
                pytest.mark.now(_BASE.isoformat()),
                pytest.mark.config(
                    TAGS_YQL_NOTIFICATION_SETTINGS={
                        'failure': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': True,
                        },
                        'upcoming_query_expiration': {
                            'is_enabled': False,
                            'auto_subscribe_query_author': True,
                            'notification_schedule': [
                                {'remaining_minutes': 10},
                                {'remaining_days': 1},
                                {'remaining_days': 2},
                                {'remaining_hours': 3},
                            ],
                        },
                        'query_expiration': {
                            'is_enabled': False,
                            'auto_subscribe_query_author': True,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            None,
            False,
            None,
            _NO_EMAIL,
            id='upcoming_expiration_disabled',
            marks=[
                pytest.mark.now(_BASE_MINUS_2_DAYS.isoformat()),
                pytest.mark.config(
                    TAGS_YQL_NOTIFICATION_SETTINGS={
                        'failure': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': True,
                        },
                        'upcoming_query_expiration': {
                            'is_enabled': False,
                            'auto_subscribe_query_author': True,
                            'notification_schedule': [
                                {'remaining_minutes': 10},
                                {'remaining_days': 1},
                                {'remaining_days': 2},
                                {'remaining_hours': 3},
                            ],
                        },
                        'query_expiration': {
                            'is_enabled': False,
                            'auto_subscribe_query_author': True,
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_yql_disposer_notifications(
        taxi_tags,
        mockserver,
        pgsql,
        last_notified_at: Optional[str],
        expect_sticker_call: bool,
        expected_last_notified_at: Optional[str],
        expected_email_xml: Optional[str],
):
    @mockserver.json_handler('/sticker/send-internal/')
    def send_internal(request):
        return mockserver.make_response('{}', 200)

    if last_notified_at:
        _set_last_notified_at(pgsql, last_notified_at)

    await tags_tools.activate_task(taxi_tags, 'yql-disposer')

    _verify_last_notified_at(pgsql, expected_last_notified_at)

    if expect_sticker_call:
        assert send_internal.times_called == 1
        send_internal_request = send_internal.next_call()['request']
        assert sorted(send_internal_request.json['send_to'].split(',')) == [
            'd-captain@yandex-team.ru',
            'loginef@yandex-team.ru',
        ]
        assert expected_email_xml is not None
        assert send_internal_request.json['body'] == expected_email_xml
    else:
        assert not send_internal.has_calls
