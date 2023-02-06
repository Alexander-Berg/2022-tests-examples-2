INSERT INTO feeds_admin.feeds
    (target_service, feed_uuid, payload, status, author)
VALUES
    ('feeds-sample', '11111111111111111111111111111111', '{"text": "Hello, {name}"}', 'created', 'vbelikov');


INSERT INTO feeds_admin.schedule
    (schedule_id, recurrence, parameters)
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
                "value": "2022-01-01T00:00:00+00:00",
                "class_": "datetime.datetime"
            }
        }'
    );


INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    ('11111111111111111111111111111111', 1, 'channels', NULL, '{}');


INSERT INTO feeds_admin.recipients
    (group_id, recipient_id)
VALUES
    (1, 'user:1'),
    (1, 'user:2'),
    (1, 'user:3');


INSERT INTO feeds_admin.run_history
    (feed_uuid, run_id, status, incremental_run_period, recipient_group_id, schedule_id, planned_start_at, created_at, updated_at)
VALUES
    ('11111111111111111111111111111111', 1, 'planned', 24, 1, 1, '2022-01-01 00:00:00Z', '1970-01-01 00:00:00Z', '1970-01-01 00:00:00+00');
