# pylint: disable=protected-access
import pytest

PARK_DRIVER_PROFILE_ID = '111222_5f348f2ca2b3c0e3d82'

UDID1 = '5f3e5b648f32ca2b3c0e3d81'
UDID2 = '5f3e5b648f32ca2b3c0e3d82'


DEFAULT_RULE = {
    'name': 'name',
    'query': (
        'SELECT unique_driver_id, '
        'countIf(seen) as seen, comment '
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
                    'tags': [{'name': 'tag3'}],
                },
            ],
        },
    ],
}


def get_rule(**kwargs):
    rule = DEFAULT_RULE.copy()
    rule.update(kwargs)
    return rule


@pytest.mark.now('2020-03-19T01:00:01')
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={
        'moscow': [
            get_rule(
                actions=[
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
            ),
        ],
        'spb': [
            get_rule(
                actions=[
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'user_phone_id',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [
                                    {'name': 'tag4'},
                                    {
                                        'name': 'tag5',
                                        'relative_ttl': {
                                            'days_offset': 0,
                                            'expire_at_time': '10:00:00',
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                ],
            ),
        ],
    },
)
async def test_stq_query_task(
        stq_runner,
        stq3_context,
        mockserver,
        mockserver_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    def response(request, *args, **kwargs):
        query = request._data.decode('UTF-8')
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': [
                {
                    'seen': 1,
                    'comment': '123',
                    'unique_driver_id': UDID1 if UDID1 in query else UDID2,
                },
            ],
            'rows': 1,
        }

    tags_mock = tags_service_mock()
    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mockserver_clickhouse_host(response, host_list[0][11:] + ':test_pass/')

    await stq_runner.driver_metrics_query_processing.call(
        task_id='query_processing_worker/0/0',
        args=[],
        kwargs={
            'log_extra': {
                'extdict': {'task_id': 'query_processing_worker/0/0'},
            },
            'events': [
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d81',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                },
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )

    assert tags_mock.passenger_tags_upload.times_called == 2
    assert tags_mock.passenger_tags_upload.next_call()['_args'][0].json == {
        'merge_policy': 'append',
        'entity_type': 'user_phone_id',
        'tags': [
            {'name': 'tag4', 'match': {'id': '5f3e5b778f32ca2b3c0e3d83'}},
            {
                'name': 'tag5',
                'match': {
                    'id': '5f3e5b778f32ca2b3c0e3d83',
                    'until': '2020-03-19T13:00:00+0300',
                },
            },
        ],
    }
    assert tags_mock.passenger_tags_upload.next_call()['_args'][0].json == {
        'entity_type': 'user_phone_id',
        'merge_policy': 'append',
        'tags': [
            {'match': {'id': '5f3e5b778f32ca2b3c0e3d83'}, 'name': 'tag3'},
        ],
    }


@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={
        'moscow': [
            get_rule(
                name='name',
                actions=[
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
            ),
            get_rule(
                name='name2',
                actions=[
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'user_phone_id',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'tag_tag_3'}],
                            },
                        ],
                    },
                ],
            ),
        ],
        'spb': [
            get_rule(
                query='SELECT unique_driver_id, '
                'countIf(seen) as seen, comment '
                'WHERE unique_driver_id in $fake',
            ),
        ],
    },
)
async def test_stq_query_task_event_fail(
        stq,
        stq_runner,
        stq3_context,
        mockserver,
        patch,
        mockserver_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    def response(*args, **kwargs):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': [{'seen': 1, 'comment': '123', 'unique_driver_id': UDID1}],
            'rows': 2,
        }

    tags_service_mock()
    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mockserver_clickhouse_host(response, host_list[0][11:] + ':test_pass/')

    await stq_runner.driver_metrics_query_processing.call(
        task_id='query_processing_worker/0/0',
        args=[],
        kwargs={
            'log_extra': {
                'extdict': {'task_id': 'query_processing_worker/0/0'},
            },
            'events': [
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d81',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'moscow',
                },
                {
                    'order_id': '123',
                    'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                },
            ],
        },
    )

    assert stq.driver_metrics_query_processing.next_call()['kwargs'] == {
        'events': [
            {
                '_rule_map': {'spb_name_None_query': False},
                'event_timestamp': 1597922316,
                'order_id': '123',
                'park_driver_profile_id': '111222_5f348f2ca2b3c0e3d82',
                'tariff_zone': 'spb',
                'unique_driver_id': '5f3e5b648f32ca2b3c0e3d82',
                'user_id': '5f3e5b778f32ca2b3c0e3d84',
                'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
            },
        ],
        'try_num': 2,
    }


@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_CH_QUERY_RULES={'spb': [get_rule()]},
)
async def test_stq_query_task_event_all_completed(
        stq_runner,
        stq3_context,
        mockserver,
        mockserver_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    def response(*args, **kwargs):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': [{'seen': 1, 'comment': '123', 'unique_driver_id': UDID1}],
            'rows': 2,
        }

    tags_mock = tags_service_mock()
    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mockserver_clickhouse_host(response, host_list[0][11:] + ':test_pass/')

    await stq_runner.driver_metrics_query_processing.call(
        task_id='query_processing_worker/0/0',
        args=[],
        kwargs={
            'log_extra': {
                'extdict': {'task_id': 'query_processing_worker/0/0'},
            },
            'events': [
                {
                    'order_id': '123',
                    'unique_driver_id': UDID1,
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'spb',
                    '_rule_map': {'spb_name_None_query': True},
                },
            ],
        },
    )
    # rules not applying because its already completed in previous run
    assert not tags_mock.passenger_tags_upload.times_called


@pytest.mark.config(
    DRIVER_METRICS_CH_QUERY_RULES={
        'moscow': [get_rule(name='name'), get_rule(name='name2')],
    },
)
async def test_stq_query_task_clickhouse_fail(stq_runner):
    with pytest.raises(RuntimeError):
        await stq_runner.driver_metrics_query_processing.call(
            task_id='query_processing_worker/0/0',
            args=[],
            kwargs={
                'log_extra': {
                    'extdict': {'task_id': 'query_processing_worker/0/0'},
                },
                'events': [
                    {
                        'order_id': '123',
                        'unique_driver_id': UDID1,
                        'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                        'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                        'user_id': '5f3e5b778f32ca2b3c0e3d84',
                        'event_timestamp': 1597922316,
                        'tariff_zone': 'moscow',
                    },
                ],
            },
        )


@pytest.mark.config(
    DRIVER_METRICS_QUERY_PROCESSING_SETTINGS={'max_tries': 3},
    DRIVER_METRICS_CH_QUERY_RULES={'moscow': [get_rule()]},
)
async def test_stq_query_task_max_tries(stq_runner):
    # error does not raise
    await stq_runner.driver_metrics_query_processing.call(
        task_id='query_processing_worker/0/0',
        args=[],
        kwargs={
            'log_extra': {
                'extdict': {'task_id': 'query_processing_worker/0/0'},
            },
            'events': [
                {
                    'order_id': '123',
                    'unique_driver_id': UDID1,
                    'park_driver_profile_id': PARK_DRIVER_PROFILE_ID,
                    'user_phone_id': '5f3e5b778f32ca2b3c0e3d83',
                    'user_id': '5f3e5b778f32ca2b3c0e3d84',
                    'event_timestamp': 1597922316,
                    'tariff_zone': 'moscow',
                },
            ],
            'try_num': 4,
        },
    )
