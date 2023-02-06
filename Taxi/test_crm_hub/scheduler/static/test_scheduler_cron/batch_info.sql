DROP TABLE IF EXISTS crm_hub.policy_test_table;
CREATE TABLE crm_hub.policy_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
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
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    log_task_id INTEGER
);

INSERT INTO crm_hub.policy_test_table
    (
        unique_driver_id,
        user_id,
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
        text,
        application
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android'
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.policy_control_test_table;
CREATE TABLE crm_hub.policy_control_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
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
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    log_task_id INTEGER
);

INSERT INTO crm_hub.policy_control_test_table
    (
        unique_driver_id,
        user_id,
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
        text,
        application
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android'
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.sending_test_table;
CREATE TABLE crm_hub.sending_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
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
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    log_task_id INTEGER
);

INSERT INTO crm_hub.sending_test_table
    (
        unique_driver_id,
        user_id,
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
        text,
        application,
        policy_allowed
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_test_table;
CREATE TABLE crm_hub.logging_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_test_table
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN 'SUCCESS'
             ELSE 'SKIP'
        END,
        FALSE,
        FALSE
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_test_wo_policy_table;
CREATE TABLE crm_hub.logging_test_wo_policy_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_test_wo_policy_table
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        NULL,
        'SUCCESS',
        FALSE,
        FALSE
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_control_table;
CREATE TABLE crm_hub.logging_control_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_control_table
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        NULL,
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN FALSE
             ELSE TRUE
        END
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_control_wo_policy_table;
CREATE TABLE crm_hub.logging_control_wo_policy_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_control_wo_policy_table
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        NULL,
        NULL,
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN FALSE
             ELSE TRUE
        END
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_by_task_id;
CREATE TABLE crm_hub.logging_by_task_id (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_by_task_id
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg,
        log_task_id
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN 'SUCCESS'
             ELSE 'SKIP'
        END,
        FALSE,
        FALSE,
        i % 3
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.logging_mixed;
CREATE TABLE crm_hub.logging_mixed (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_mixed
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg,
        log_task_id
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN 'SUCCESS'
             ELSE 'SKIP'
        END,
        FALSE,
        FALSE,
        CASE WHEN i <= 150 THEN i % 3
            ELSE NULL
        END
    FROM generate_series(1, 200) as i
);


DROP TABLE IF EXISTS crm_hub.logging_test_expired_table;
CREATE TABLE crm_hub.logging_test_expired_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    experiment_id TEXT,
    text TEXT,
    application TEXT,
    policy_allowed BOOLEAN,
    was_logged BOOLEAN,
    status TEXT,
    reason TEXT,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    log_task_id INTEGER
);

INSERT INTO crm_hub.logging_test_expired_table
    (
        unique_driver_id,
        user_id,
        group_id,
        group_name,
        db_id,
        driver_uuid,
        phone,
        city,
        country,
        locale,
        experiment_id,
        text,
        application,
        policy_allowed,
        status,
        control_flg,
        global_control_flg
    )
(
    SELECT
        'driver_' || i::TEXT,
        'user_phone_' || i::TEXT,
        'driver_' || i::TEXT,
        '',
        'dbid' || i::TEXT,
        'driveruuid' || i::TEXT,
        '',
        '',
        '',
        '',
        '',
        'driver_' || i::TEXT,
        'android',
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        NULL,
        FALSE,
        FALSE
    FROM generate_series(1, 200) as i
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
    'policy_test_table',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000001',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000002',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000003',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
    'wall',
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
    TRUE,
    FALSE,
    'group_name'
),
(
    '00000000000000000000000000000004',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_control_table',
    '',
    'driver',
    'control',
    'wall',
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
    TRUE,
    'group_name'
),
(
    '00000000000000000000000000000005',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_control_wo_policy_table',
    '',
    'driver',
    'control',
    'wall',
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
    TRUE,
    'group_name'
),
(
    '00000000000000000000000000000006',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_wo_policy_table',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000007',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_by_task_id',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000008',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_mixed',
    '',
    'driver',
    'testing',
    'wall',
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
),
(
    '00000000000000000000000000000009',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'policy_control_test_table',
    '',
    'driver',
    'testing',
    'wall',
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
    TRUE,
    'group_name'
);
