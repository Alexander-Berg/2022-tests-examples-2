DROP TABLE IF EXISTS crm_hub.sending_test_table;
CREATE TABLE crm_hub.sending_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    global_control_flg TEXT,
    experiment_id TEXT,
    text TEXT DEFAULT 'sample text',
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'sample title',
    url TEXT DEFAULT 'ya.ru',
    dsat_action TEXT DEFAULT 'ya.ru',
    teaser TEXT DEFAULT 'sample teaser'
);

INSERT INTO crm_hub.sending_test_table
    (
        unique_driver_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        global_control_flg,
        experiment_id,
        application,
        policy_allowed
    )
(
    SELECT
        'driver_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'db_id_' || i::TEXT,
        'driver_uuid_' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        '',
        'android',
        TRUE
    FROM generate_series(1, 10) as i
);

INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    entity_type,
    group_type,
    channel,
    channel_info,
    processing_chunk_size,
    use_policy,
    extra_data,
    extra_data_path,
    created_at,
    subfilters,
    sending_stats,
    start_id,
    replication_state,
    verify,
    control,
    group_name
) VALUES
(
    '00000000000000000000000000000000',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
    'legacywall',
    '{"channel_name": "driver_wall"}'::jsonb,
    30,
    TRUE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    FALSE,
    'group_name'
);
