import pytest

from tests_subventions_activity_producer import common
from tests_subventions_activity_producer import pg_helpers
from tests_subventions_activity_producer import redis_helpers


async def _run_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        taxi_config,
        messages,
        **additional_settings,
):
    await common.set_logbroker_messages(
        taxi_subventions_activity_producer, messages,
    )

    await common.run_message_fetcher_once(
        taxi_subventions_activity_producer, taxi_config, **additional_settings,
    )


def _check_raw_driver_events_grouped(
        load_json, pgsql, datafiles_expected_by_shard,
):
    for i, datafile in enumerate(datafiles_expected_by_shard):
        expected = load_json(datafile)
        schema = 'shard{}'.format(i)
        actual = pg_helpers.get_raw_driver_events_grouped(pgsql, schema)
        assert expected == actual, 'Unexpected data for shard #{}'.format(i)


@pytest.mark.parametrize(
    'init_docs,messages_doc,expected_docs',
    [
        pytest.param(
            # init_docs
            [],
            # messages_doc
            'default_input_messages.json',
            # expected_docs
            [
                'common_expected_raw_event_groups_shard0.json',
                'common_expected_raw_event_groups_shard1.json',
                'common_expected_raw_event_groups_shard2.json',
            ],
            id='common',
        ),
        pytest.param(
            # init_docs
            [],
            # messages_doc
            'default_input_messages.json',
            # expected_docs
            [
                'change_interval_expected_raw_event_groups_shard0.json',
                'change_interval_expected_raw_event_groups_shard1.json',
                'change_interval_expected_raw_event_groups_shard2.json',
            ],
            id='change_interval',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_ACTIVITY_PRODUCER_AGGREGATION_INTERVAL=[
                        {
                            'time_point': '2019-10-11T13:40:00+03:00',
                            'length_min': 5,
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            # init_docs
            [
                'handle_updated_init_raw_event_groups_shard0.json',
                'empty_shard.json',
                'empty_shard.json',
            ],
            # messages_doc
            'handle_updated_input_messages.json',
            # expected_docs
            [
                'handle_updated_expected_raw_event_groups_shard0.json',
                'empty_shard.json',
                'empty_shard.json',
            ],
            id='handle_updated_field',
        ),
        pytest.param(
            # init_docs
            [],
            # messages_doc
            'add_billing_types_messages.json',
            # expected_docs
            [
                'add_billing_types_raw_event_groups_shard0.json',
                'empty_shard.json',
                'empty_shard.json',
            ],
            id='handle_updated_field',
        ),
    ],
)
@pytest.mark.now('2019-10-11T13:41:00+03:00')
async def test_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        pgsql,
        taxi_config,
        init_docs,
        messages_doc,
        expected_docs,
):
    pg_helpers.init_raw_driver_events_grouped(
        load_json, pgsql, datafiles_by_shard=init_docs,
    )

    messages = load_json(messages_doc)
    await _run_message_fetcher(
        taxi_subventions_activity_producer, testpoint, taxi_config, messages,
    )

    _check_raw_driver_events_grouped(
        load_json, pgsql, datafiles_expected_by_shard=expected_docs,
    )


@pytest.mark.now('2019-10-11T13:41:00+03:00')
async def test_message_fetcher_exceed_db_size(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        pgsql,
        taxi_config,
):
    @testpoint('db_size_exceeded')
    def db_size_exceeded(request):
        return {'skip_db_writing': True}

    @testpoint('writing_to_db')
    def writing_to_db(request):
        return {}

    pg_helpers.init_raw_driver_events_grouped(
        load_json, pgsql, datafiles_by_shard=['init_raw_events_grouped.json'],
    )

    messages = load_json('default_input_messages.json')
    await _run_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        taxi_config,
        messages,
        db_raw_events_grouped_max_size=3,
    )

    assert db_size_exceeded.times_called > 0
    assert writing_to_db.times_called == 0


@pytest.mark.parametrize(
    'messages_doc,migrated,expected_doc',
    [
        pytest.param(
            # messages_doc
            'default_input_messages.json',
            # migrated
            False,
            # expected_doc
            'default_expected_redis_state.json',
            id='default',
        ),
        pytest.param(
            # messages_doc
            'add_billing_types_messages.json',
            # migrated
            False,
            # expected_doc
            'add_billing_types_expected_redis_state.json',
            id='add_billing_types',
        ),
        pytest.param(
            # messages_doc
            'incomplete_messages.json',
            # migrated
            True,
            # expected_doc
            'incomplete_messages_expected_redis_state.json',
            id='incomplete_messages',
        ),
    ],
)
@pytest.mark.now('2019-10-11T13:41:00+03:00')
async def test_message_fetcher_redis(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        pgsql,
        redis_store,
        taxi_config,
        messages_doc,
        migrated,
        expected_doc,
):
    if migrated:
        taxi_config.set_values(
            {
                'SUBVENTIONS_ACTIVITY_PRODUCER_REDIS_MIGRATION': {
                    'use_uuid_as_key_since': '2019-10-11T13:38:00+03:00',
                },
            },
        )

    messages = load_json(messages_doc)
    await _run_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        taxi_config,
        messages,
        enable_redis=True,
    )

    expected = load_json(expected_doc)
    actual = redis_helpers.get_state_as_doc(redis_store)
    assert expected == actual


@pytest.mark.now('2019-10-11T13:41:00+03:00')
async def test_message_fetcher_exceed_redis_db_size(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        redis_store,
        taxi_config,
):
    @testpoint('db_size_exceeded')
    def db_size_exceeded(request):
        return {'skip_db_writing': True}

    @testpoint('writing_to_db')
    def writing_to_db(request):
        return {}

    redis_helpers.prepare_storage(redis_store, load_json('init_redis.json'))

    messages = load_json('default_input_messages.json')
    await _run_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        taxi_config,
        messages,
        enable_redis=True,
        enable_postgres=False,
        db_redis_max_size=20,
    )

    assert db_size_exceeded.times_called > 0
    assert writing_to_db.times_called == 0


@pytest.mark.config(
    SUBVENTIONS_ACTIVITY_PRODUCER_REDIS_MIGRATION={
        'use_uuid_as_key_since': '2019-10-11T13:40:00+03:00',
    },
)
@pytest.mark.now('2019-10-11T13:41:00+03:00')
async def test_message_fetcher_redis_migration_udid_to_dbid_uuid(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        pgsql,
        redis_store,
        taxi_config,
):
    messages = load_json('default_input_messages.json')
    await _run_message_fetcher(
        taxi_subventions_activity_producer,
        testpoint,
        taxi_config,
        messages,
        enable_redis=True,
    )

    expected = load_json('migrated_expected_redis_state.json')
    actual = redis_helpers.get_state_as_doc(redis_store)
    assert expected == actual
