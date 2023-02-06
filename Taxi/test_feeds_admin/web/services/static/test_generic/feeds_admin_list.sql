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
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('cities:Moscow', 1),
    ('cities:Novosibirsk', 1),
    ('cities:Moscow', 4),
    ('cities:Novosibirsk', 4);

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, schedule_id, name, payload, status, created, author
    )
VALUES
    (
        'driver_wall',
        '11111111111111111111111111111111',
        1,
        'bar',
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        '1971-01-01 19:11:25+00'::timestamp with time zone,
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        1,
        'bar is {param1}, {param2}',
        '{"text": "foo is {param1}", "title": "bar is {param1}, {param2}", "type": "dsat"}'::jsonb,
        'created',
        '1972-01-01 19:11:25+00'::timestamp with time zone,
        'lostpointer'
    ),
    (
        'driver_wall',
        '33333333333333333333333333333333',
        1,
        'bar',
        '{"text": "foo", "title": "bar"}'::jsonb,
        'deleted',
        '1973-01-01 19:11:25+00'::timestamp with time zone,
        'adomogashev'
    ),
    (
        'driver_wall',
        '44444444444444444444444444444444',
        1,
        'бары',
        '{"text": "foo", "title": "bar", "type": "newsletter"}'::jsonb,
        'error',
        '1974-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'driver_wall',
        '55555555555555555555555555555555',
        1,
        'bar',
        '{"text": "foo", "title": "bar", "type": "newsletter"}'::jsonb,
        'finished',
        '1975-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'payload-filter',
        '66666666666666666666666666666666',
        1,
        NULL,
        '{"text": "equals text", "type": "newsletter"}'::jsonb,
        'created',
        '1976-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'payload-filter',
        '77777777777777777777777777777777',
        1,
        NULL,
        '{"content": {"name": "like this name"}, "type": "newsletter"}'::jsonb,
        'created',
        '1977-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'payload-filter',
        '88888888888888888888888888888888',
        1,
        NULL,
        '{"content": {"name": "or similar to this name"}, "type": "newsletter"}'::jsonb,
        'created',
        '1978-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'payload-filter',
        '99999999999999999999999999999999',
        1,
        NULL,
        '{"content": {"name": "it''s has and escaping"}, "type": "newsletter"}'::jsonb,
        'created',
        '1979-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
    ),
    (
        'payload-filter',
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        1,
        NULL,
        '{"pages": [{"name": "array"}]}'::jsonb,
        'created',
        '1980-01-01 19:11:25+00'::timestamp with time zone,
        'v-belikov'
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
