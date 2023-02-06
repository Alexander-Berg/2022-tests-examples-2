INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'yql'::feeds_admin.recipient_group_type,
        'some_yql',
        NULL
    ),
    (
        '22222222222222222222222222222222',
        20,
        'yql'::feeds_admin.recipient_group_type,
        'some_yql',
        NULL
    ),
    (
        '33333333333333333333333333333333',
        30,
        'yql'::feeds_admin.recipient_group_type,
        'some_yql',
        NULL
    ),
    (
        '44444444444444444444444444444444',
        40,
        'yql'::feeds_admin.recipient_group_type,
        'some_yql',
        NULL
    ),
    (
        '55555555555555555555555555555555',
        50,
        'yql'::feeds_admin.recipient_group_type,
        'some_yql',
        NULL
    );

INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1, -- too soon: 0 days until expiration
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "3000-01-02T01:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        2, -- just in time: 1 day until expiration
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-03T01:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        3, -- between two sending: 2 days until expiration
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-04T01:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        4, -- just in time: 3 days until expiration
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-05T01:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        5, -- not soon enough: 4 days until expiration
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-06T01:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        6, -- already finished: short-lived
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T20:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-01T21:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        7, -- already finished, but lived for a very long time
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "1970-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2000-01-01T21:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    );


INSERT INTO feeds_admin.feeds
    (
        target_service,
        feed_uuid,
        schedule_id,
        name,
        settings,
        payload,
        status,
        author,
        created,
        updated
    )
VALUES
    (
        'test_service',
        '11111111111111111111111111111111',
        1,
        'name1',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'published',
        'adomogashev',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '22222222222222222222222222222222',
        2,
        'name2',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'published',
        'adomogashev',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '33333333333333333333333333333333',
        3,
        'name3',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'published',
        'adomogashev',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '44444444444444444444444444444444',
        4,
        'name4',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'published',
        'adomogashev',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '55555555555555555555555555555555',
        5,
        'name5',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'published',
        'adomogashev',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '66666666666666666666666666666666',
        6,
        'name6',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'finished',
        'adomogashev',
        '2000-01-01 12:00:00+0300'::timestamp with time zone,
        '2000-01-01 13:00:00+0300'::timestamp with time zone
    ),
    (
        'test_service',
        '77777777777777777777777777777777',
        7,
        'name7',
        '{}'::jsonb,
        '{"key": "value"}'::jsonb,
        'finished',
        'adomogashev',
        '1970-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 13:00:00+0300'::timestamp with time zone
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, planned_start_at, created_at, updated_at, status
    )
VALUES
    (
        '11111111111111111111111111111111',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '22222222222222222222222222222222',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '33333333333333333333333333333333',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '44444444444444444444444444444444',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '55555555555555555555555555555555',
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 00:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '66666666666666666666666666666666',
        '2000-01-01 20:00:00+0300'::timestamp with time zone,
        '2000-01-01 20:00:00+0300'::timestamp with time zone,
        '2000-01-01 21:00:00+0300'::timestamp with time zone,
        'success'
    ),
    (
        '77777777777777777777777777777777',
        '1970-01-01 00:00:00+0300'::timestamp with time zone,
        '1970-01-01 00:00:00+0300'::timestamp with time zone,
        '2000-01-01 21:00:00+0300'::timestamp with time zone,
        'success'
    );
