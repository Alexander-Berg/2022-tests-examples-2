INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
        'once',
        '{
            "ttl": {
                "value": {
                    "value": 86400.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            },
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:11:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    );

INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        1,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '22222222222222222222222222222222',
        2,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '44444444444444444444444444444444',
        4,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '55555555555555555555555555555555',
        5,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '66666666666666666666666666666666',
        6,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '77777777777777777777777777777777',
        7,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    );

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, schedule_id, payload, status, author
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        1,
        '{"text": "foo is {param1}", "title": "bar is {param1}, {param2}", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        1,
        '{"text": "foo", "title": "bar", "url": "{param1}", "teaser": "{param1}", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '44444444444444444444444444444444',
        1,
        '{"text": "foo is {param1}", "title": "bar is {param1}, {param2}", "type": "dsat"}'::jsonb,
        'publishing',
        'adomogashev'
    ),
    (
        'driver_wall',
        '55555555555555555555555555555555',
        1,
        '{"text": "foo", "title": "bar", "type": "dsat"}'::jsonb,
        'publishing',
        'adomogashev'
    ),
    (
        'driver_wall',
        '66666666666666666666666666666666',
        1,
        '{"text": "foo", "title": "bar", "type": "dsat"}'::jsonb,
        'publishing',
        'adomogashev'
    ),
    (
        'feeds-sample',
        '77777777777777777777777777777777',
        1,
        '{"text": "text with {param1}"}'::jsonb,
        'publishing',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, run_id, recipient_count, status, created_at, planned_start_at, updated_at
    )
VALUES
    (
        '11111111111111111111111111111111',
        1,
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '22222222222222222222222222222222',
        2,
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '44444444444444444444444444444444',
        4,
        0,
        'in_progress',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '55555555555555555555555555555555',
        5,
        0,
        'in_progress',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '66666666666666666666666666666666',
        6,
        0,
        'in_progress',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '77777777777777777777777777777777',
        7,
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    );
