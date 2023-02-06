INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, payload, status, author
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        '{"text": "foo", "title": "bar", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        '{"text": "foo", "title": "bar", "type": "dsat"}'::jsonb,
        'created',
        'adomogashev'
    );


INSERT INTO feeds_admin.recipient_group
    (group_id, group_type, yql_link, group_settings)
VALUES
    (
        1,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "drivers"}'::jsonb
    ),
    (
        2,
        'yql'::feeds_admin.recipient_group_type,
        'https://yql.yandex-team.ru/Operations/XcMgbglcTqZ0aVYUubyZry3e4_PdRxX85UTpzl3ENzo=',
        NULL
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('db_id__uuid1', 1),
    ('db_id__uuid2', 1);

INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "3000-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        2,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "3000-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    );

INSERT INTO feeds_admin.run_history
    (
        run_id, feed_uuid, recipient_group_id, schedule_id, recipient_count, status, created_at, planned_start_at, updated_at
    )
VALUES
    (
        1,
        '11111111111111111111111111111111',
        1,
        1,
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:10:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    ),
    (
        2,
        '22222222222222222222222222222222',
        2,
        2,
        NULL,
        'planned',
        '1970-01-01 00:00:00+00'::timestamp with time zone,
        '2018-06-22 19:10:25-07'::timestamp with time zone,
        '1970-01-01 00:00:00+00'::timestamp with time zone
    );
