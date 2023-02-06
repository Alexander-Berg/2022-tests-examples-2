#  pylint: disable=protected-access
import pytest

from taxi_driver_metrics.common.models import query_processor
from taxi_driver_metrics.common.models.rules import rule_utils


PARK_DRIVER_PROFILE_ID = '111222_5f348f2ca2b3c0e3d82'


@pytest.mark.translations(
    taximeter_messages={
        'driverpush.DriverMessageReceivedMessageTitle': {
            'ru': 'Сообщение пришло',
            'fr': 'Meesagous recifed',
            'en': 'Message received',
        },
    },
)
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={
        rule_utils.CONFIG_DEFAULT: [
            {
                'name': 'name',
                'query': (
                    'SELECT unique_driver_id, '
                    'countIf(seen) as seen, comment '
                    'from $order_metrics '
                    'WHERE unique_driver_id in $unique_driver_ids'
                ),
                'actions': [
                    {
                        'expr': """ qr['comment'] == 'good' """,
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'dbid_uuid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag1'}],
                            },
                            {
                                'type': 'tagging',
                                'entity_type': 'udid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag1'}],
                            },
                            {
                                'type': 'push',
                                'code': 1300,
                                'tanker_key_template': (
                                    'driverpush.DriverMessageReceivedMessage'
                                ),
                                'keyset': 'taximeter_messages',
                                'action': 'Получить',
                                'action_link': 'link://yes',
                                'system_notification': True,
                            },
                        ],
                    },
                    {
                        'expr': """ qr['seen'] > 5 """,
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'user_id',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag2'}],
                            },
                        ],
                    },
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'user_phone_id',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag3'}],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'name2',
                'disabled': True,
                'query': (
                    'SELECT unique_driver_id, '
                    'countIf(seen) as seen, comment '
                    'from $order_metrics '
                    'WHERE unique_driver_id in $unique_driver_ids'
                ),
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'user_phone_id',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag8'}],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
@pytest.mark.parametrize('comment', ['good', 'bad'])
@pytest.mark.parametrize('seen', [3, 10])
async def test_different_entities(
        stq3_context,
        mock_clickhouse_host,
        mockserver,
        tags_service_mock,
        response_mock,
        comment,
        seen,
):
    @mockserver.json_handler('/client-notify/v2/push')
    async def send_push(*args, **kwargs):
        data = args[0].json

        assert data == {
            'client_id': '111222-5f348f2ca2b3c0e3d82',
            'intent': 'Получить',
            'notification': {
                'link': 'link://yes',
                'text': {
                    'key': 'driverpush.DriverMessageReceivedMessageMessage',
                    'keyset': 'taximeter_messages',
                },
                'title': {
                    'key': 'driverpush.DriverMessageReceivedMessageTitle',
                    'keyset': 'taximeter_messages',
                },
            },
            'service': 'taximeter',
            'data': {
                'action': 'Получить',
                'code': 1300,
                'priority': 'high',
                'system_notification': True,
                'need_notification': True,
            },
        }
        return

    tag_mock = tags_service_mock()
    response_json = {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'seen': seen,
                'comment': comment,
                'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
            },
            {
                'seen': seen,
                'comment': comment,
                'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
            },
        ],
        'rows': 1,
    }

    def response(*args, **kwargs):
        return response_mock(json=response_json)

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(response, host_list[0])

    await query_processor.process_events(
        stq3_context,
        events=[
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                },
            ),
        ],
    )
    if comment == 'bad':
        assert tag_mock.passenger_tags_upload.times_called
    else:
        assert send_push.times_called
        assert tag_mock.tags_upload.times_called


@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={
        rule_utils.CONFIG_DEFAULT: [
            {
                'name': 'name',
                'query': (
                    'SELECT unique_driver_id, '
                    'countIf(seen) as seen, comment '
                    'from $order_metrics '
                    'WHERE unique_driver_id in $unique_driver_ids'
                ),
                'actions': [],
            },
        ],
    },
)
async def test_query_rules_empty_identifiers(
        stq3_context,
        mock_clickhouse_host,
        mockserver,
        tags_service_mock,
        response_mock,
):
    # error does not raise
    await query_processor.process_events(
        stq3_context,
        events=[
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': None,
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                },
            ),
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                },
            ),
        ],
    )


@pytest.mark.translations(
    taximeter_messages={
        'driverpush.DriverMessageReceivedMessageTitle': {
            'ru': 'Сообщение пришло',
            'fr': 'Meesagous recifed',
            'en': 'Message received',
        },
    },
)
@pytest.mark.parametrize(
    'event, result',
    (
        (
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                    'event_type': 'order',
                    'event_key': 'handle_driver_die',
                    'event_id': 'yes',
                },
            ),
            False,
        ),
        (
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                    'event_type': 'order',
                    'event_key': 'handle_complete',
                    'event_id': 'yes',
                },
            ),
            True,
        ),
        (
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                    'event_type': 'order',
                    'event_key': 'handle_complete',
                    'event_id': 'no',
                },
            ),
            False,
        ),
        (
            query_processor.CompletableByRuleEvent(
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                    'event_type': 'rapesition',
                    'event_key': 'handle_post_finish',
                    'event_id': 'no_yes',
                },
            ),
            True,
        ),
    ),
)
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={
        rule_utils.CONFIG_DEFAULT: [
            {
                'name': 'name',
                'query': (
                    'SELECT unique_driver_id, '
                    'countIf(seen) as seen, comment '
                    'from $order_metrics '
                    'WHERE unique_driver_id in $unique_driver_ids'
                ),
                'events': [{'topic': 'order', 'name': 'handle_complete'}],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'udid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag1'}],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'name2',
                'query': (
                    'SELECT unique_driver_id, '
                    'countIf(seen) as seen, comment '
                    'from $order_metrics '
                    'WHERE unique_driver_id in $unique_driver_ids'
                ),
                'events': [{'name': 'handle_post_finish'}],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'udid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag8'}],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_events_rules(
        stq3_context,
        mock_clickhouse_host,
        mockserver,
        tags_service_mock,
        response_mock,
        event,
        result,
):
    tag_mock = tags_service_mock()

    response_json = {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'seen': 10,
                'comment': 'ha',
                'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                'triggered_event_ids': ['yes', 'no_yes'],
            },
        ],
        'rows': 1,
    }

    def response(*args, **kwargs):
        return response_mock(json=response_json)

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(response, host_list[0])

    await query_processor.process_events(stq3_context, events=[event])
    assert bool(tag_mock.tags_upload.times_called) is result
