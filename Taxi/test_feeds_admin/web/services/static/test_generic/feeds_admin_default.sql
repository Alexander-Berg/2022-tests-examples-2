INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 86400.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        2,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:11:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 172800.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        3,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:11:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 259200.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        4,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:11:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 345600.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        5,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:11:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 432000.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        6,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 86400.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    );

INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        1,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
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
        '33333333333333333333333333333333',
        3,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    ),
    (
        '44444444444444444444444444444444',
        4,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
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
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('city:Moscow;page:main;position:all', 1),
    ('city:Novosibirsk;page:news;position:all', 1),
    ('city:Moscow', 4),
    ('city:Novosibirsk', 4),
    ('city:Moscow;page:main;position:all', 6),
    ('city:Novosibirsk;page:news;position:all', 6);

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, schedule_id, payload, status, author, settings, name
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        1,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev',
        NULL,
        NULL
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        2,
        '{"text": "foo is {param1}", "title": "bar is {param1}, {param2}", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev',
        NULL,
        NULL
    ),
    (
        'driver_wall',
        '33333333333333333333333333333333',
        3,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'deleted',
        'adomogashev',
        NULL,
        NULL
    ),
    (
        'driver_wall',
        '44444444444444444444444444444444',
        4,
        '{"text": "foo", "title": "bar", "type": "newsletter"}'::jsonb,
        'error',
        'adomogashev',
        NULL,
        NULL
    ),
    (
        'driver_wall',
        '55555555555555555555555555555555',
        5,
        '{"text": "foo", "title": "bar", "type": "newsletter"}'::jsonb,
        'finished',
        'adomogashev',
        NULL,
        NULL
    ),
    (
        'driver_wall',
        '66666666666666666666666666666666',
        6,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev',
        '{
            "priority": 1,
            "screens": ["main", "payment"],
            "extra": {
                "subobject": "ok"
            }
        }'::jsonb,
        '{param1}'
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, started_at, finished_at, status, error_reason, message
    )
VALUES
    (
        '44444444444444444444444444444444',
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        'success',
        NULL,
        NULL
    ),
    (
        '44444444444444444444444444444444',
        '2018-06-23 19:11:25-07'::timestamp with time zone,
        '2018-06-23 19:11:25-07'::timestamp with time zone,
        'error',
        'internal',
        'Random error text'
    )
