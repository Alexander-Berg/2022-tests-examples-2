INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    ),
    (
        '33333333333333333333333333333333',
        30,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    ),
    (
        '44444444444444444444444444444444',
        40,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 10),
    ('Novosibirsk', 10),
    ('Moscow', 30),
    ('Novosibirsk', 30),
    ('Krasnoyarsk', 30),
    ('Lipetsk', 30),
    ('Ufa', 40),
    ('Murmansk', 40);

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
    );

INSERT INTO feeds_admin.feeds
    (
        target_service, feed_uuid, recipient_group_id, schedule_id, payload, status, author
    )
VALUES
    (
        'feeds-sample',
        '44444444444444444444444444444444',
        40,
        10,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'eats-promotions-story',
        '11111111111111111111111111111111',
        10,
        NULL,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'eats-promotions-story',
        '22222222222222222222222222222222',
        NULL,
        NULL,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    ),
    (
        'eats-promotions-story',
        '33333333333333333333333333333333',
        30,
        NULL,
        '{"text": "foo", "title": "bar"}'::jsonb,
        'created',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (feed_uuid, run_id, status, incremental_run_period, recipient_group_id, schedule_id, planned_start_at, created_at, updated_at)
VALUES
    ('44444444444444444444444444444444', 50, 'planned', 24, 40, 10, '2019-08-27T10:00:00', '2019-08-27T10:00:00', '2019-08-27T10:00:00');
