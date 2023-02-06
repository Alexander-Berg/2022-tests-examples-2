async def run_task(taxi_eats_eaters):
    await taxi_eats_eaters.run_task('data-mappings-upload')


def initialize_meta_table(psql_cursor):
    psql_cursor.execute(
        'INSERT INTO eats_eaters.edm_upload_state'
        '(id, last_updated_at, last_id, last_run_at)'
        'VALUES(1, \'2020-06-15T12:00:00+00:00\', 0,'
        '\'-infinity\'::timestamp)',
    )


DEFAULT_CREATED_AT = '2018-06-14T14:00:00+00:00'


def insert_eater(psql_cursor, user_id, updated_at, created_at=None):
    insert_begin = (
        'INSERT INTO eats_eaters.users'
        '(id, passport_uid, client_id, personal_email_id, personal_phone_id,'
        'updated_at, created_at, client_type)'
    )
    psql_cursor.execute(
        insert_begin
        + user_values(
            user_id,
            updated_at,
            created_at if created_at else DEFAULT_CREATED_AT,
        ),
    )


def user_values(user_id, updated_at, created_at):
    return (
        'VALUES({user_id}, \'yandex_uid_{user_id}\', \'uuid_{user_id}\','
        '\'pmail_id_{user_id}\', \'ppid_{user_id}\', \'{updated_at}\','
        '\'{created_at}\', \'no matter\')'.format(
            user_id=user_id, updated_at=updated_at, created_at=created_at,
        )
    )


def user_expected(expected_data):
    if isinstance(expected_data, list):
        res = []
        for user_data in expected_data:
            res.extend(_user_expected(user_data))
        return res

    return _user_expected(expected_data)


def _user_expected(user_data):
    user_id = user_data
    created_at = DEFAULT_CREATED_AT

    if isinstance(user_data, tuple):
        user_id = user_data[0]
        created_at = user_data[1]

    return [
        {
            'first_entity_type': 'eater_id',
            'first_entity_value': str(user_id),
            'second_entity_type': 'yandex_uid',
            'second_entity_value': 'yandex_uid_' + str(user_id),
            'created_at': created_at,
        },
        {
            'first_entity_type': 'eater_id',
            'first_entity_value': str(user_id),
            'second_entity_type': 'personal_email_id',
            'second_entity_value': 'pmail_id_' + str(user_id),
            'created_at': created_at,
        },
        {
            'first_entity_type': 'eater_id',
            'first_entity_value': str(user_id),
            'second_entity_type': 'eater_uuid',
            'second_entity_value': 'uuid_' + str(user_id),
            'created_at': created_at,
        },
        {
            'first_entity_type': 'eater_id',
            'first_entity_value': str(user_id),
            'second_entity_type': 'personal_phone_id',
            'second_entity_value': 'ppid_' + str(user_id),
            'created_at': created_at,
        },
    ]


def mock_now(mock_now_value):
    return {
        'mock_now': 'TIMESTAMP WITH TIME ZONE \'{}\''.format(
            mock_now_value.strftime('%Y-%m-%dT%H:%M:%S%z'),
        ),
    }


def get_last_updated_at(psql_cursor):
    psql_cursor.execute(
        'SELECT last_updated_at '
        'FROM eats_eaters.edm_upload_state '
        'WHERE id = 1;',
    )
    updated_ats = list(x[0] for x in psql_cursor)
    return updated_ats[0]


def get_default_config(chunk_size=2):
    return {
        'default_params': {
            'upload_period_ms': 1000,
            'upload_chunk_size': 15,
            'read_delay_sec': 600,
            'network_timeout_ms': 600,
            'statement_timeout_ms': 600,
        },
        'eats-eaters': {
            'upload_period_ms': 500,
            'upload_chunk_size': chunk_size,
            'read_delay_sec': 120,
            'network_timeout_ms': 500,
            'statement_timeout_ms': 500,
        },
    }


def start_mode_patch_config(start_from_now=True):
    def _start_mode_patch_config(config, config_vars):
        if start_from_now:
            config['components_manager']['components'][
                'data-mappings-uploader'
            ]['start_from_the_very_beginning'] = False
        else:
            config['components_manager']['components'][
                'data-mappings-uploader'
            ]['start_from_the_very_beginning'] = True

    return _start_mode_patch_config


async def get_metric(taxi_eats_eaters_monitor, with_real_run_period=True):
    # Data sending
    sent_data = await taxi_eats_eaters_monitor.get_metric('sent-data')
    interpolated_chunk_size = await taxi_eats_eaters_monitor.get_metric(
        'interpolated-chunk-size',
    )

    # Chunk size limits
    chunk_size_limit = await taxi_eats_eaters_monitor.get_metric(
        'chunk-size-limit',
    )
    data_to_send_in_minute_limit = await taxi_eats_eaters_monitor.get_metric(
        'data-to-send-in-minute-limit',
    )

    # Delays
    sync_delay_real = await taxi_eats_eaters_monitor.get_metric(
        'sync-delay-real-sec',
    )
    sync_delay_offset = await taxi_eats_eaters_monitor.get_metric(
        'sync-delay-offset-sec',
    )

    # Run period
    run_period_ms = await taxi_eats_eaters_monitor.get_metric('run-period-ms')
    real_run_period_ms = await taxi_eats_eaters_monitor.get_metric(
        'real-run-period-ms',
    )
    step_time_ms = await taxi_eats_eaters_monitor.get_metric('step-time-ms')

    has_metrics = {
        'sent-data': sent_data,
        'interpolated-chunk-size': interpolated_chunk_size,
        'chunk-size-limit': chunk_size_limit,
        'data-to-send-in-minute-limit': data_to_send_in_minute_limit,
        'sync-delay-real-sec': sync_delay_real,
        'sync-delay-offset-sec': sync_delay_offset,
        'run-period-ms': run_period_ms,
        'step-time-ms': step_time_ms,
    }

    if with_real_run_period:
        has_metrics['real-run-period-ms'] = real_run_period_ms

    return has_metrics
