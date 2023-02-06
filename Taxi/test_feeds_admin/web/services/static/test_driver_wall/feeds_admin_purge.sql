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
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    ),
    (
        '33333333333333333333333333333333',
        3,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 1),
    ('Novosibirsk', 1),
    ('Moscow', 2),
    ('Novosibirsk', 2),
    ('Moscow', 3),
    ('Novosibirsk', 3);


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
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        3,
        'once',
        '{
            "ttl": {
                "value": {
                    "value": 259200.0,
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
        '{
            "title": "Заголовок",
            "text": "Текст **markdown** с {параметрами}",
            "url": "https://yandex.ru",
            "teaser": "Текст на ссылке",
            "type": "newsletter",
            "dom_storage": true,
            "notification_mode": "normal",
            "important": false,
            "alert": true,
            "format": "Markdown",
            "url_open_mode": "browser"
        }'::jsonb,
        'published',
        'adomogashev'
    ),
    (
        'driver_wall',
        '22222222222222222222222222222222',
        2,
        '{
            "title": "Заголовок",
            "text": "Текст **markdown** с {параметрами}",
            "url": "https://yandex.ru",
            "teaser": "Текст на ссылке",
            "type": "newsletter",
            "dom_storage": true,
            "notification_mode": "normal",
            "important": false,
            "alert": true,
            "format": "Markdown",
            "url_open_mode": "browser"
        }'::jsonb,
        'error',
        'adomogashev'
    ),
    (
        'driver_wall',
        '33333333333333333333333333333333',
        3,
        '{
            "title": "Заголовок",
            "text": "Текст **markdown** с {параметрами}",
            "url": "https://yandex.ru",
            "teaser": "Текст на ссылке",
            "type": "newsletter",
            "dom_storage": true,
            "notification_mode": "normal",
            "important": false,
            "alert": true,
            "format": "Markdown",
            "url_open_mode": "browser"
        }'::jsonb,
        'finished',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, created_at, finished_at, status, error_reason, message
    )
VALUES
    (
        '11111111111111111111111111111111',
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        'success',
        NULL,
        NULL
    ),
    (
        '22222222222222222222222222222222',
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        NULL,
        'planned',
        NULL,
        NULL
    );
