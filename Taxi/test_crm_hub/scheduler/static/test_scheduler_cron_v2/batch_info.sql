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
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    actions_states JSONB,
    policy_group TEXT
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
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    actions_states JSONB,
    policy_group TEXT
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
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    title TEXT DEFAULT 'title',
    url TEXT DEFAULT 'url',
    teaser TEXT DEFAULT 'teaser',
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
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
        actions_states,
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
        CASE WHEN i % 2 = 1 THEN '{"policy": {"status": "SUCCESS", "source_task_id": 123}, "driver_sms": {"status": "SUCCESS"},
                                  "user_push": {"status": "SUCCESS"}, "user_sms": {"status": "SUCCESS"},
                                  "driver_push": {"status": "SUCCESS"}, "driver_legacywall": {"status": "SUCCESS"}}'::jsonb
             ELSE '{"policy": {"status": "SKIP", "source_task_id": 123}, "driver_sms": {"status": "SKIP"}, "user_push": {"status": "SKIP"},
                   "user_sms": {"status": "SKIP"}, "driver_push": {"status": "SKIP"},
                   "driver_legacywall": {"status": "SKIP"}}'::jsonb
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
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
        application,
        actions_states,
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
        'android',
        '{"driver_sms": {"status": "SUCCESS", "source_task_id": 123}}'::jsonb,
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    actions JSONB,
    policy_group TEXT
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
        application,
        actions_states,
        control_flg,
        global_control_flg,
        actions
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
        'android',
        CASE WHEN i % 2 = 1 THEN '{"policy": {"status": "SUCCESS", "source_task_id": 123}}'::jsonb
             ELSE '{"policy": {"status": "SKIP", "source_task_id": 123}}'::jsonb
        END,
        CASE WHEN i % 2 = 1 THEN TRUE
             ELSE FALSE
        END,
        CASE WHEN i % 2 = 1 THEN FALSE
             ELSE TRUE
        END,
        '{}'::jsonb
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
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
        application,
        actions_states,
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
        'android',
        NULL,
        NULL,
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
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
        application,
        actions_states,
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
        'android',
        CASE WHEN i % 2 = 1 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": ' || (i % 3)::TEXT || '}, "driver_sms": {"status": "SUCCESS"}}')::jsonb
             ELSE ('{"policy": {"status": "SKIP", "source_task_id": ' || (i % 3)::TEXT || '}, "driver_sms": {"status": "SKIP"}}')::jsonb
        END,
        FALSE,
        FALSE
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
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
        application,
        control_flg,
        global_control_flg,
        actions_states
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
        'android',
        FALSE,
        FALSE,
        CASE WHEN i % 2 = 1 AND i <= 150 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": ' || (i % 3)::TEXT || '}, "driver_sms": {"status": "SUCCESS"}}')::jsonb
             WHEN i % 2 != 1 AND i <= 150 THEN ('{"policy": {"status": "SKIP", "source_task_id": '|| (i % 3)::TEXT ||'}, "driver_sms": {"status": "SKIP"}}')::jsonb
             WHEN i % 2 != 1 AND i > 150 THEN ('{"policy": {"status": "SKIP", "source_task_id": 123}, "driver_sms": {"status": "SKIP"}}')::jsonb
             WHEN i % 2 = 1 AND i > 150 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": 123}, "driver_sms": {"status": "SUCCESS"}}')::jsonb
             ELSE NULL
        END
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.sending_finished_test_table;
CREATE TABLE crm_hub.sending_finished_test_table (
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
);

INSERT INTO crm_hub.sending_finished_test_table
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
        application,
        control_flg,
        global_control_flg,
        actions_states
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
        'android',
        FALSE,
        FALSE,
        CASE WHEN i % 2 = 1 AND i <= 150 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": ' || (i % 3)::TEXT || '}, "driver_sms": {"status": "FAIL", "reason": "reason"}}')::jsonb
             WHEN i % 2 != 1 AND i <= 150 THEN ('{"policy": {"status": "SKIP", "source_task_id": '|| (i % 3)::TEXT ||'}}')::jsonb
             WHEN i % 2 != 1 AND i > 150 THEN ('{"policy": {"status": "DENIED", "source_task_id": 123}}')::jsonb
             WHEN i % 2 = 1 AND i > 150 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": 123}, "driver_sms": {"status": "SUCCESS"}}')::jsonb
             ELSE NULL
        END
    FROM generate_series(1, 200) as i
);

DROP TABLE IF EXISTS crm_hub.promocode_logging_without_creative_test_table;
CREATE TABLE crm_hub.promocode_logging_without_creative_test_table (
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
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    control_flg BOOLEAN,
    global_control_flg BOOLEAN,
    actions_states JSONB,
    policy_group TEXT
);

INSERT INTO crm_hub.promocode_logging_without_creative_test_table
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
        application,
        actions_states,
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
        'android',
        '{"promocode": {"status": "SUCCESS", "source_task_id": 123}}'::jsonb,
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
    group_name,
    actions
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_legacywall"}
        },
        {
            "action_name": "policy",
            "channel": "legacywall"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000001',
    1234,
    1234,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'user',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_promo",
                            "content": "promo_id", "ticket": "ticket"}
        },
        {
            "action_name": "policy",
            "channel": "promo"
        }
    ]')::jsonb
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_legacywall"}
        },
        {
            "action_name": "policy",
            "channel": "legacywall"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000010',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000011',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000012',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_push",
                            "content": "my_content",
                            "deeplink": "my_deeplink",
                            "code": 100,
                            "ttl": 30,
                            "collapse_key": "MessageNew:test",
                            "title": "title"}
        },
        {
            "action_name": "policy",
            "channel": "push"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000013',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_push",
                            "intent": "none",
                            "content": "my_content",
                            "deeplink": "my_deeplink",
                            "ttl": 30,
                            "title": "title"}
        },
        {
            "action_name": "policy",
            "channel": "push"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000014',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_legacywall",
                            "text": "text",
                            "type": "type",
                            "url": "url",
                            "title": "title",
                            "teaser": "teaser"}
        },
        {
            "action_name": "policy",
            "channel": "legacywall"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000015',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_control_table',
    '',
    'driver',
    'control',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000016',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000017',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000018',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_push",
                            "content": "my_content",
                            "deeplink": "my_deeplink",
                            "code": 100,
                            "ttl": 30,
                            "collapse_key": "MessageNew:test",
                            "title": "title"}
        },
        {
            "action_name": "policy",
            "channel": "push"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000019',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_push",
                            "intent": "none",
                            "content": "my_content",
                            "deeplink": "my_deeplink",
                            "ttl": 30,
                            "title": "title"}
        },
        {
            "action_name": "policy",
            "channel": "push"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000020',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_legacywall",
                            "text": "text",
                            "type": "type",
                            "url": "url",
                            "title": "title",
                            "teaser": "teaser"}
        },
        {
            "action_name": "policy",
            "channel": "legacywall"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000021',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_control_wo_policy_table',
    '',
    'driver',
    'control',
    30,
    FALSE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    TRUE,
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000022',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'logging_test_wo_policy_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000023',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'user',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_promo",
                            "content": "promo_id", "ticket": "ticket"}
        },
        {
            "action_name": "policy",
            "channel": "promo"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000024',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_finished_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "driver_sms",
                            "intent": "none",
                            "sender": "sender",
                            "content": "my_content"}
        },
        {
            "action_name": "policy",
            "channel": "sms"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000025',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'promocode_logging_without_creative_test_table',
    '',
    'driver',
    'testing',
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
    'group_name',
    ('[
        {
           "action_name": "promocode",
           "promocode_settings":
            {
                "service": "eats",
                "series": "series_1",
                "finish_at": "2022-01-31T04:00:00+03:00"
            }
       }
    ]')::jsonb
);
