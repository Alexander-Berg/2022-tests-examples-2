import json

import pytest

from tests_subventions_events_filter import helpers
from . import test_common


def _make_message(timestamp):
    data = {
        'drivers': [
            {'unique_driver_id': 'udid1', 'dbid': 'dbid1', 'uuid': 'uuid1'},
        ],
        'timestamp': timestamp,
        'tariff_zone': 'msc',
        'tags': ['driver_tag'],
        'payment_type_restrictions': 'none',
        'geoarea': 'msc',
    }
    return json.dumps(data)


@pytest.mark.parametrize(
    'message_time,expected_tags_request',
    [
        pytest.param(
            # message_time
            '2020-01-01T12:00:30+00:00',
            # expected_tags_request
            [
                {
                    'match': {'id': 'dbid1_uuid1', 'ttl': 30},
                    'name': 'supertag',
                },
                {
                    'match': {'id': 'dbid1_uuid1', 'ttl': 150},
                    'name': 'ultratag',
                },
            ],
            id='normal',
        ),
        pytest.param(
            # message_time
            '2020-01-01T12:00:00+00:00',
            # expected_tags_request
            [{'match': {'id': 'dbid1_uuid1', 'ttl': 120}, 'name': 'ultratag'}],
            id='expire-one-tag',
        ),
        pytest.param(
            # message_time
            '2020-01-01T11:58:00+00:00',
            # expected_tags_request
            None,
            id='expire-both-tags',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_SETTINGS={
        'enabled': False,
        'bulk_size': 100,
        'enable_tagging': True,
        'logbroker_producer_settings': {
            'max_in_fly_messages': 11,
            'partitions_number': 2,
            'commit_timeout': 100,
        },
        'logbroker_consumer_settings': {
            'enabled': True,
            'queue_timeout': 100,
            'chunk_size': 100,
            'config_poll_period': 1000,
        },
    },
    SUBVENTIONS_EVENTS_FILTER_TAGGING_RULES={
        'default_tag_ttl_s': 60,
        'rules': [{'tag': 'supertag'}, {'tag': 'ultratag', 'ttl_s': 180}],
    },
)
@pytest.mark.now('2020-01-01T12:01:00+0000')
async def test_tagging(
        taxi_subventions_events_filter,
        testpoint,
        mockserver,
        message_time,
        expected_tags_request,
):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        subventions = [test_common.RULES_SELECT_RULE]
        return {'subventions': subventions}

    @mockserver.json_handler('/tags/v1/upload')
    def _mock_v1_upload(request):
        doc = request.json
        assert doc == {
            'entity_type': 'dbid_uuid',
            'merge_policy': 'append',
            'tags': expected_tags_request,
        }
        return {'status': 'ok'}

    await test_common.send_message(
        taxi_subventions_events_filter,
        testpoint,
        _make_message(timestamp=message_time),
    )

    if expected_tags_request is not None:
        await _mock_v1_upload.wait_call()


@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_SETTINGS={
        'enabled': False,
        'bulk_size': 100,
        'enable_tagging': False,
        'enable_saving_data_to_redis': True,
        'logbroker_producer_settings': {
            'max_in_fly_messages': 11,
            'partitions_number': 2,
            'commit_timeout': 100,
        },
        'logbroker_consumer_settings': {
            'enabled': True,
            'queue_timeout': 100,
            'chunk_size': 100,
            'config_poll_period': 1000,
        },
    },
    SUBVENTIONS_EVENTS_FILTER_TAGGING_RULES={
        'default_tag_ttl_s': 60,
        'rules': [{'tag': 'mock_tag_1'}, {'tag': 'mock_tag_2', 'ttl_s': 180}],
    },
)
@pytest.mark.parametrize(
    'redis_state,messages,expected_redis_state',
    [
        (
            # redis_state
            {},
            # messages
            [_make_message(timestamp='2020-01-01T12:00:30+0000')],
            # expected_redis_state
            {
                'tag:mock_tag_1:udid1': '2020-01-01T12:00:30+0000',
                'tag:mock_tag_2:udid1': '2020-01-01T12:00:30+0000',
            },
        ),
        (
            # redis_state
            {'tag:mock_tag_1:udid1': '2020-01-01T11:55:51+00:00'},
            # messages
            [
                _make_message(timestamp='2020-01-01T12:00:30+0000'),
                _make_message(timestamp='2020-01-01T12:00:38+0000'),
            ],
            # expected_redis_state
            {
                'tag:mock_tag_1:udid1': '2020-01-01T12:00:38+0000',
                'tag:mock_tag_2:udid1': '2020-01-01T12:00:38+0000',
            },
        ),
    ],
)
async def test_save_data_into_redis(
        taxi_subventions_events_filter,
        mockserver,
        testpoint,
        load_json,
        redis_store,
        redis_state,
        messages,
        expected_redis_state,
):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        subventions = [test_common.RULES_SELECT_RULE]
        return {'subventions': subventions}

    helpers.set_redis_state(redis_store, redis_state)

    for msg in messages:
        await test_common.send_message(
            taxi_subventions_events_filter, testpoint, msg,
        )

    assert helpers.get_redis_state(redis_store) == expected_redis_state
