# pylint: disable=W0621
import datetime
import json

import pytest

from taxi.stq import async_worker_ng

from rider_metrics.stq import processing


BASE_RMS_URL = '/rider-metrics-storage/'
UNPROCESSED_LIST_URL = f'{BASE_RMS_URL}v2/events/unprocessed/list'
DEFAULT_GEO_NODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_world',
        'name_en': 'World',
        'name_ru': 'Мир',
        'node_type': 'root',
        'parent_name': 'br_root',
        'tariff_zones': ['br_izhevsk', 'moscow'],
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'root',
        'parent_name': 'br_root',
        'tariff_zones': ['sub_moscow'],
    },
    {
        'name': 'br_izhevsk',
        'name_en': 'Izhevsk',
        'name_ru': 'Ижевск',
        'node_type': 'root',
        'parent_name': 'br_world',
        'tariff_zones': ['rivendell'],
        'region_id': '44',
    },
]
UNPROCESSED_LIST_RESPONSE = {
    'items': [
        {
            'user_id': 'cool_user',
            'ticket_id': 68,
            'events': [
                {
                    'event_id': 3,
                    'created': datetime.datetime.utcnow().isoformat(),
                    'type': 'order',
                    'tariff_zone': 'rivendell',
                    'extra_data': {'user_id': 'user_id'},
                },
            ],
        },
        {
            'user_id': 'cool_user_2',
            'ticket_id': 69,
            'events': [
                {
                    'event_id': 4,
                    'created': datetime.datetime.utcnow().isoformat(),
                    'type': 'order',
                    'tariff_zone': 'rivendell',
                    'extra_data': {'park_profile_id': 'fake_park_id'},
                },
            ],
        },
        {
            'user_id': 'cool_user_3',
            'ticket_id': 70,
            'events': [
                {
                    'event_id': 5,
                    'created': datetime.datetime.utcnow().isoformat(),
                    'type': 'order',
                    'tariff_zone': 'rivendell',
                    'extra_data': {'park_profile_id': 'fake_park_id'},
                },
            ],
        },
        {
            'user_id': 'cool_user_4',
            'ticket_id': 70,
            'events': [
                {
                    'event_id': 5,
                    'created': datetime.datetime.utcnow().isoformat(),
                    'type': 'order',
                    'tariff_zone': 'rivendell',
                    'extra_data': {'park_profile_id': 'fake_park_id'},
                },
            ],
        },
    ],
}

UNPROCESSED_LIST_RESPONSE_DRIVER = {
    'items': [
        {
            'user_id': 'cool_user',
            'ticket_id': 68,
            'events': [
                {
                    'event_id': 3,
                    'created': datetime.datetime.utcnow().isoformat(),
                    'type': 'order',
                    'tariff_zone': 'default',
                    'extra_data': {'park_profile_id': 'fake_park_id'},
                },
            ],
        },
    ],
}


RIDER_HISTORY = [
    {
        'event_id': 0,
        'created': '2019-12-19T11:50:36.898890',
        'type': 'order',
        'extra_data': json.dumps({'user_id': 'user_id'}),
        'descriptor': '{"name": "complete"}',
    },
    {
        'event_id': 1,
        'created': '2019-12-19T11:51:35.898890',
        'type': 'order',
        'extra_data': json.dumps({'user_id': 'user_id'}),
        'descriptor': '{"name": "complete"}',
    },
    {
        'event_id': 2,
        'created': '2019-12-19T11:52:34.898890',
        'type': 'order',
        'extra_data': json.dumps({'user_id': 'user_id'}),
        'descriptor': '{"name": "complete"}',
    },
]


def get_unprocessed_list(user_id):
    return {
        'items': [
            {
                'user_id': user_id,
                'ticket_id': 68,
                'events': [
                    {
                        'event_id': 3,
                        'created': datetime.datetime.utcnow().isoformat(),
                        'type': 'order',
                        'extra_data': {'user_id': user_id},
                    },
                ],
            },
        ],
    }


@pytest.fixture
def run_processing_task(stq3_context):
    async def _run_task(task_id):
        await processing.task(
            stq3_context,
            task_info=async_worker_ng.TaskInfo(
                id=task_id,
                exec_tries=0,
                reschedule_counter=0,
                queue='rider_metrics_processing',
            ),
        )

    return _run_task


async def test_task(mockserver, run_processing_task, stq):
    @mockserver.json_handler(UNPROCESSED_LIST_URL)
    async def _mock_unprocessed_list(*_args, **_kwargs):
        return {'items': []}

    await run_processing_task('slave/2/9')
    await run_processing_task('master')
    assert (
        stq.rider_metrics_processing.times_called == 11
    )  # 10 slaves and 1 master reschedule


@pytest.mark.geo_nodes(DEFAULT_GEO_NODES)
@pytest.mark.config(
    RIDER_METRICS_RULES={
        'node:br_root': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'tags::bndrnk AND tags:rasul '
                            'WILL event:crash_service'
                        ),
                    },
                ],
                'name': 'unique4',
            },
            {
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                        'tags': (
                            'tags::drop_taxi_if_exist and event::get_all_money'
                        ),
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'unique3',
            },
            {
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'tags': 'event::trying_to_destroy service',
                'name': 'unique2',
            },
            {
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'user_id',
                            },
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'unique',
            },
        ],
    },
    RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
)
async def test_processing_scenario(
        taxi_config, mock_processing_service, run_processing_task,
):
    patch = mock_processing_service(
        UNPROCESSED_LIST_RESPONSE, ['tag1', 'tag3'],
    )
    await run_processing_task('slave/1/1')

    assert patch.communications.times_called
    communications_call = patch.communications.next_call()['_args'][0].json
    del communications_call['event_timestamp']
    assert communications_call == {
        'campaign_id': 'communication_69',
        'entity_id': 'user_id',
        'event_id': '3',
        'extra_data': {'user_id': 'user_id'},
    }


@pytest.mark.config(
    RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    RIDER_METRICS_HISTORY_LIMIT_CLASSES=[
        {'class': 'limit_0_class', 'entity_ids': ['user_id', 'user_0']},
        {'class': 'limit_10_class', 'entity_ids': ['user_10']},
    ],
    RIDER_METRICS_HISTORY_LIMIT_SETTINGS={
        '__default__': {'limit': 1000},
        'limit_0_class': {},
        'limit_10_class': {'limit': 10},
    },
)
@pytest.mark.now('2019-09-11T12:08:12')
@pytest.mark.parametrize(
    'user_id, history_call_result',
    (
        (
            'user_0',
            {
                'created_after': '2019-09-11T02:08:12+03:00',
                'user_id': 'user_0',
            },
        ),
        (
            'user_10',
            {
                'created_after': '2019-09-11T02:08:12+03:00',
                'user_id': 'user_10',
                'limit': 10,
            },
        ),
        (
            'user_default',
            {
                'created_after': '2019-09-11T02:08:12+03:00',
                'user_id': 'user_default',
                'limit': 1000,
            },
        ),
    ),
)
async def test_processing_history_limits(
        taxi_config,
        mock_processing_service,
        run_processing_task,
        user_id,
        history_call_result,
):
    patch = mock_processing_service(get_unprocessed_list(user_id), [])
    await run_processing_task('slave/1/1')

    assert (
        history_call_result == patch.event_history.next_call()['_args'][0].json
    )


@pytest.mark.config(
    RIDER_METRICS_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'park_profile_id',
                            },
                            {
                                'type': 'tagging',
                                'entity_type': 'dbid_uuid',
                                'tags': [{'name': 'test_tag'}],
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule_name',
                'tags': '\'rider::driver_tag\'',
            },
        ],
    },
)
async def test_processing_driver_scenario(
        mock_processing_service, run_processing_task,
):
    patch = mock_processing_service(
        UNPROCESSED_LIST_RESPONSE_DRIVER, ['driver_tag'],
    )
    await run_processing_task('slave/1/1')

    assert patch.communications.times_called
    assert patch.driver_tags_upload.times_called

    communications_call = patch.communications.next_call()['_args'][0].json
    tags_call = patch.driver_tags_upload.next_call()['_args'][0].json
    assert tags_call == {
        'merge_policy': 'append',
        'entity_type': 'dbid_uuid',
        'tags': [{'name': 'test_tag', 'match': {'id': 'fake_park_id'}}],
    }
    del communications_call['event_timestamp']
    assert communications_call == {
        'campaign_id': 'communication_69',
        'entity_id': 'fake_park_id',
        'event_id': '3',
        'extra_data': {'park_profile_id': 'fake_park_id'},
    }


@pytest.mark.now('2019-12-19T11:53:35.898890')
@pytest.mark.config(
    RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True,
    RIDER_METRICS_TAG_FOR_EXPERIMENT={
        'common_tag': {'salt': 'pepper', 'from': 0, 'to': 100},
    },
)
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'park_profile_id',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule1',
                'tags': '\'experiment::common_tag\'',
                'events_to_trigger_cnt': 10,
            },
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'tags': [{'name': 'test_tag'}],
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule2',
                'events_to_trigger_cnt': 2,
            },
            {
                'id': '3',
                'zone': 'default',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'tags': [{'name': 'test_tag_60_sec'}],
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule3',
                'events_to_trigger_cnt': 2,
                'events_period_sec': 60,
            },
            {
                'id': '4',
                'zone': 'default',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'tags': [{'name': 'test_tag_simple'}],
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule4',
            },
            {
                'id': '4',
                'zone': 'default',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'tags': [{'name': 'test_tag_180sec'}],
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'rule5',
                'events_to_trigger_cnt': 4,
                'events_period_sec': 180,
            },
        ],
    },
)
async def test_processing_scenario_thresholds(
        mock_processing_service, run_processing_task,
):
    patch = mock_processing_service(
        UNPROCESSED_LIST_RESPONSE,
        ['tag1', 'tag3'],
        events_history=RIDER_HISTORY,
    )
    await run_processing_task('slave/1/1')

    assert not patch.communications.times_called

    assert patch.event_complete.times_called

    tagging_calls = []
    for _ in range(patch.tags_match.times_called):
        next_call = patch.tags_match.next_call()
        tagging_calls.append(next_call['_args'][0].json)
    for _ in range(patch.tags_upload.times_called):
        next_call = patch.tags_upload.next_call()
        tagging_calls.append(next_call['_args'][0].json)

    assert sorted(tagging_calls, key=str) == [
        {'entities': [{'id': 'cool_user', 'type': 'user_phone_id'}]},
        {'entities': [{'id': 'cool_user_2', 'type': 'user_phone_id'}]},
        {'entities': [{'id': 'cool_user_3', 'type': 'user_phone_id'}]},
        {'entities': [{'id': 'cool_user_4', 'type': 'user_phone_id'}]},
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [{'match': {'id': 'cool_user'}, 'name': 'test_tag'}],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [{'match': {'id': 'cool_user_2'}, 'name': 'test_tag'}],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [{'match': {'id': 'cool_user_3'}, 'name': 'test_tag'}],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [{'match': {'id': 'cool_user_4'}, 'name': 'test_tag'}],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user'}, 'name': 'test_tag_180sec'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_2'}, 'name': 'test_tag_180sec'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_3'}, 'name': 'test_tag_180sec'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_4'}, 'name': 'test_tag_180sec'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user'}, 'name': 'test_tag_simple'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_2'}, 'name': 'test_tag_simple'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_3'}, 'name': 'test_tag_simple'},
            ],
        },
        {
            'entity_type': 'user_phone_id',
            'merge_policy': 'append',
            'tags': [
                {'match': {'id': 'cool_user_4'}, 'name': 'test_tag_simple'},
            ],
        },
    ]
