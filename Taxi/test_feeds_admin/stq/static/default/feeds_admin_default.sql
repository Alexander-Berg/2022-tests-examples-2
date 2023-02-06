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
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        2,
        'once',
        '{
            "ttl": {
                "value": {
                    "value": 172800.0,
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
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    ),
    (
        '22222222222222222222222222222222',
        2,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        '{}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 1),
    ('Novosibirsk', 1);

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, schedule_id, payload, status, author
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        1,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        2,
        '{"text": "foo is {param1}", "title": "bar is {param1}, {param2}", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, recipient_count, status, created_at, planned_start_at, updated_at
    )
VALUES
    (
        '11111111111111111111111111111111',
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:10:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        '22222222222222222222222222222222',
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    )
