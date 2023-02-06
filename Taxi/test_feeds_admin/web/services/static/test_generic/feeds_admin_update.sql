INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        10,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2020-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 86400000.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        20,
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
        30,
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
        40,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 86400000.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            }
        }'
    ),
    (
        50,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Once",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "ttl": {
                "value": {
                    "value": 86400000.0,
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
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('cities:Moscow', 1),
    ('cities:Novosibirsk', 1),
    ('cities:Moscow', 4),
    ('cities:Novosibirsk', 4),
    ('cities:Moscow', 5),
    ('cities:Novosibirsk', 5);

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, schedule_id, payload, status, author
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        10,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        20,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '33333333333333333333333333333333',
        30,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'deleted',
        'adomogashev'
    ),
    (
        'driver_wall',
        '44444444444444444444444444444444',
        40,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '55555555555555555555555555555555',
        50,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (
        run_id, feed_uuid, planned_start_at, status
    )
VALUES
    (10, '11111111111111111111111111111111','2020-06-22 19:10:25-07'::timestamptz, 'planned'),
    (20, '22222222222222222222222222222222','2018-06-22 19:11:25-07'::timestamptz, 'in_progress'),
    (40, '44444444444444444444444444444444','2018-06-22 19:11:25-07'::timestamptz, 'success'),
    (41, '44444444444444444444444444444444','2020-06-22 19:11:25-07'::timestamptz, 'planned'),
    (50, '55555555555555555555555555555555','2018-06-22 19:11:25-07'::timestamptz, 'planned')
