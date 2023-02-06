import functools
import json

import pytest

_MESSAGE_FETCHER_TESTSUITE_TASK = 'online-events-consumer-lb_consumer'

_EVENTS_SENDER_TASK = 'events-sender-0'
_ACTIVITY_PRODUCER_PG_TASK = 'activity-producer-pg-0'
_ACTIVITY_PRODUCER_REDIS_TASK = 'activity-producer-redis-0'
_EVENTS_FIXER_TASK = 'incomplete-events-fixer-0'
_EVENTS_VERIFICATOR_TASK = 'activity-events-verificator-0'

_PERIODIC_TASKS = [
    _EVENTS_SENDER_TASK,
    _ACTIVITY_PRODUCER_PG_TASK,
    _ACTIVITY_PRODUCER_REDIS_TASK,
    _EVENTS_FIXER_TASK,
    _EVENTS_VERIFICATOR_TASK,
]


def suspend_all_periodic_tasks(func):
    @pytest.mark.suspend_periodic_tasks(*_PERIODIC_TASKS)
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapped


async def _update_config(
        service,
        taxi_config,
        fetcher_enabled=False,
        aggregation_enabled=False,
        events_sender_enabled=False,
        events_fixer_enabled=False,
        events_verificator_enabled=False,
        time_diff=None,
        aggregate_delay_ms=None,
        db_activity_events_unsent_max_size=None,
        db_redis_max_size=None,
        db_raw_events_grouped_max_size=None,
        mf_enable_postgres=None,
        mf_enable_redis=None,
        ap_enable_redis=None,
        ap_enable_postgres=None,
        ap_gather_complete_info_redis=None,
        ap_destinations=None,
        es_billing_types_to_send_to_bte=None,
        es_events_chunk_size=None,
        es_drop_events_on_400=None,
        ev_check_delay_s=None,
        j_tags_topics=None,
):
    conf_sap = {
        'message_fetcher_settings': {
            'enabled': fetcher_enabled,
            'logbroker_consumer': {
                'queue_timeout_ms': 100,
                'chunk_size': 100,
                'config_poll_period_ms': 1000,
            },
            'sleep_interval_ms': 50,
            'pg_queries_settings': {
                'statement_timeout_ms': 250,
                'execute_timeout_ms': 250,
            },
        },
        'aggregation_settings': {
            'enabled': aggregation_enabled,
            'aggregate_delay_ms': (
                aggregate_delay_ms if aggregate_delay_ms else 1000
            ),
            'sleep_interval_ms': 50,
            'events_max_timediff_s': (time_diff if time_diff else 10),
            'max_missing_in_a_row': 1,
            'aggregate_algorithm': 'generalized',
            'pg_queries_settings': {
                'statement_timeout_ms': 250,
                'execute_timeout_ms': 250,
            },
            'worker_on_redis': {
                'enabled': False,
                'destinations': ['activity_events_unsent'],
            },
            'worker_on_postgres': {
                'enabled': True,
                'destinations': ['activity_events_unsent'],
            },
        },
        'events_sender_settings': {
            'enabled': events_sender_enabled,
            'sleep_interval_ms': 50,
            'events_chunk_size': 10,
            'pg_queries_settings': {
                'statement_timeout_ms': 250,
                'execute_timeout_ms': 250,
            },
        },
        'events_fixer_settings': {
            'enabled': events_fixer_enabled,
            'sleep_interval_ms': 50,
            'events_chunk_size': 5,
            'pg_queries_settings': {
                'statement_timeout_ms': 250,
                'execute_timeout_ms': 250,
            },
            'clients_chunk_sizes': {'activity': 5, 'tags': 5},
        },
        'metrics_gatherer_settings': {'enabled': False},
        'events_verificator_settings': {
            'enabled': events_verificator_enabled,
            'sleep_interval_ms': 50,
            'events_chunk_size': 10,
            'check_delay_s': 60,
        },
    }

    if db_activity_events_unsent_max_size is not None:
        conf_sap['aggregation_settings'][
            'db_activity_events_unsent_max_size'
        ] = db_activity_events_unsent_max_size

    if db_raw_events_grouped_max_size is not None:
        conf_sap['message_fetcher_settings'][
            'db_raw_events_grouped_max_size'
        ] = db_raw_events_grouped_max_size

    if db_redis_max_size is not None:
        conf_sap['message_fetcher_settings'][
            'db_redis_max_size'
        ] = db_redis_max_size

    if mf_enable_redis is not None:
        conf_sap['message_fetcher_settings']['enable_redis'] = mf_enable_redis

    if mf_enable_postgres is not None:
        conf_sap['message_fetcher_settings'][
            'enable_postgres'
        ] = mf_enable_postgres

    if ap_enable_redis is not None:
        conf_sap['aggregation_settings']['worker_on_redis'][
            'enabled'
        ] = ap_enable_redis

    if ap_enable_postgres is not None:
        conf_sap['aggregation_settings']['worker_on_postgres'][
            'enabled'
        ] = ap_enable_postgres

    if ap_gather_complete_info_redis is not None:
        conf_sap['aggregation_settings'][
            'gather_info_across_event_group_in_redis'
        ] = ap_gather_complete_info_redis

    if ap_destinations is not None:
        conf_sap['aggregation_settings']['worker_on_redis'][
            'destinations'
        ] = ap_destinations
        conf_sap['aggregation_settings']['worker_on_postgres'][
            'destinations'
        ] = ap_destinations

    if es_billing_types_to_send_to_bte is not None:
        conf_sap['events_sender_settings'][
            'billing_types_to_send_to_bte'
        ] = es_billing_types_to_send_to_bte

    if es_events_chunk_size is not None:
        conf_sap['events_sender_settings'][
            'events_chunk_size'
        ] = es_events_chunk_size

    if es_drop_events_on_400 is not None:
        conf_sap['events_sender_settings'][
            'drop_events_on_400'
        ] = es_drop_events_on_400

    if ev_check_delay_s is not None:
        conf_sap['events_verificator']['check_delay_s'] = ev_check_delay_s

    conf_joint = {}

    if j_tags_topics is not None:
        conf_joint['tags_topics'] = j_tags_topics

    taxi_config.set_values(
        dict(
            SUBVENTIONS_ACTIVITY_PRODUCER_SERVICE_SETTINGS=conf_sap,
            SUBVENTIONS_SCR_AND_SAP_JOINT_SETTINGS=conf_joint,
        ),
    )

    await service.invalidate_caches()


async def enable_message_fetcher(
        service,
        taxi_config,
        db_raw_events_grouped_max_size=None,
        db_redis_max_size=None,
        enable_redis=None,
        enable_postgres=None,
):
    await _update_config(
        service,
        taxi_config,
        fetcher_enabled=True,
        db_raw_events_grouped_max_size=db_raw_events_grouped_max_size,
        db_redis_max_size=db_redis_max_size,
        mf_enable_postgres=enable_postgres,
        mf_enable_redis=enable_redis,
    )


async def disable_message_fetcher(service, taxi_config):
    await _update_config(service, taxi_config, fetcher_enabled=False)


async def run_message_fetcher_once(service, taxi_config, *args, **kwargs):
    await enable_message_fetcher(service, taxi_config, *args, **kwargs)
    await service.run_task(_MESSAGE_FETCHER_TESTSUITE_TASK)
    await disable_message_fetcher(service, taxi_config)


async def enable_activity_producer(
        service,
        taxi_config,
        time_diff=10,
        aggregate_delay_ms=None,
        db_activity_events_unsent_max_size=None,
        enable_redis=None,
        enable_postgres=None,
        gather_info_across_event_group_in_redis=None,
        destinations=None,
):
    await _update_config(
        service,
        taxi_config,
        aggregation_enabled=True,
        time_diff=time_diff,
        aggregate_delay_ms=aggregate_delay_ms,
        db_activity_events_unsent_max_size=db_activity_events_unsent_max_size,
        ap_destinations=destinations,
        ap_enable_redis=enable_redis,
        ap_enable_postgres=enable_postgres,
        ap_gather_complete_info_redis=gather_info_across_event_group_in_redis,
    )


async def disable_activity_producer(service, taxi_config):
    await _update_config(service, taxi_config, aggregation_enabled=False)


async def run_activity_producer_once(service, taxi_config, *args, **kwargs):
    await enable_activity_producer(service, taxi_config, *args, **kwargs)
    await service.run_periodic_task(_ACTIVITY_PRODUCER_PG_TASK)
    await service.run_periodic_task(_ACTIVITY_PRODUCER_REDIS_TASK)
    await disable_activity_producer(service, taxi_config)


async def enable_events_sender(
        service,
        taxi_config,
        billing_types_to_send_to_bte=None,
        events_chunk_size=None,
        drop_events_on_400=None,
):
    await _update_config(
        service,
        taxi_config,
        events_sender_enabled=True,
        es_billing_types_to_send_to_bte=billing_types_to_send_to_bte,
        es_events_chunk_size=events_chunk_size,
        es_drop_events_on_400=drop_events_on_400,
    )


async def run_events_sender_once(service, taxi_config, *args, **kwargs):
    await enable_events_sender(service, taxi_config, *args, **kwargs)
    await service.run_periodic_task(_EVENTS_SENDER_TASK)
    await disable_events_sender(service, taxi_config)


async def disable_events_sender(service, taxi_config):
    await _update_config(service, taxi_config, events_sender_enabled=False)


async def enable_events_fixer(service, taxi_config, tags_topics=None):
    await _update_config(
        service,
        taxi_config,
        events_fixer_enabled=True,
        j_tags_topics=tags_topics,
    )


async def disable_events_fixer(service, taxi_config):
    await _update_config(service, taxi_config, events_fixer_enabled=False)


async def run_events_fixer_once(service, taxi_config, *args, **kwargs):
    await enable_events_fixer(service, taxi_config, *args, **kwargs)
    await service.run_periodic_task(_EVENTS_FIXER_TASK)
    await disable_events_fixer(service, taxi_config)


async def enable_events_verificator(service, taxi_config, check_delay_s=None):
    await _update_config(
        service,
        taxi_config,
        events_verificator_enabled=True,
        ev_check_delay_s=check_delay_s,
    )


async def disable_events_verificator(service, taxi_config):
    await _update_config(
        service, taxi_config, events_verificator_enabled=False,
    )


async def run_events_verificator_once(service, taxi_config, *args, **kwargs):
    await enable_events_verificator(service, taxi_config, *args, **kwargs)
    await service.run_periodic_task(_EVENTS_VERIFICATOR_TASK)
    await disable_events_verificator(service, taxi_config)


async def enable_full_pipeline(service, taxi_config):
    await _update_config(
        service,
        taxi_config,
        fetcher_enabled=True,
        aggregation_enabled=True,
        events_sender_enabled=True,
    )


async def disable_full_pipeline(service, taxi_config):
    await _update_config(
        service,
        taxi_config,
        fetcher_enabled=False,
        aggregation_enabled=False,
        events_sender_enabled=False,
    )


def _convert_messages(pg_messages):
    messages = []
    for pg_msg in pg_messages:
        msg = {}
        msg['consumer'] = 'online-events-consumer'
        msg['topic'] = 'online-events'
        msg['cookie'] = 'cookie1'
        msg['data'] = json.dumps(pg_msg['data'])
        messages.append(json.dumps(msg))
    return messages


async def set_logbroker_messages(taxi_subventions_activity_producer, messages):
    lb_messages = _convert_messages(messages)
    for message in lb_messages:
        await taxi_subventions_activity_producer.post(
            'tests/logbroker/messages', data=message,
        )


def get_raw_driver_events_grouped(pgsql, cluster, schema):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """SELECT dbid_uuid,chunk_ts,driver_data,timestamps,*
         FROM {}.raw_driver_events_grouped
         ORDER BY (dbid_uuid, chunk_ts);""".format(
            schema,
        ),
    )
    raw_rows = list(cursor)
    return [(row[0], row[1].isoformat(), row[2], row[3]) for row in raw_rows]
