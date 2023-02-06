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
        '{}'::jsonb
    ),
    (
        '33333333333333333333333333333333',
        3,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    ),
    (
        '44444444444444444444444444444444',
        4,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 1),
    ('Novosibirsk', 1),
    ('cities:Moscow', 2),
    ('cities:Novosibirsk', 2),
    ('Moscow', 3),
    ('Novosibirsk', 3),
    ('Moscow', 4),
    ('Novosibirsk', 4);


INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
        'schedule',
        '{
            "ttl": {
                "value": {
                    "value": 86400.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            },
            "class_": "feeds_admin.models.schedule.Weekly",
            "starts": [
                {
                    "day": 0,
                    "time": {
                        "value": "16:11:00+00:00",
                        "class_": "datetime.time"
                    },
                    "class_": "feeds_admin.models.schedule.DayOfWeek"
                }
            ],
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2022-06-22T19:10:25-07:00",
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
        'schedule',
        '{
            "ttl": {
                "value": {
                    "value": 259200.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            },
            "class_": "feeds_admin.models.schedule.Weekly",
            "starts": [
                {
                    "day": 2,
                    "time": {
                        "value": "16:11:00+00:00",
                        "class_": "datetime.time"
                    },
                    "class_": "feeds_admin.models.schedule.DayOfWeek"
                }
            ],
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2022-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    ),
    (
        4,
        'schedule',
        '{
            "ttl": {
                "value": {
                    "value": 345600.0,
                    "class_": "datetime.timedelta"
                },
                "class_": "feeds_admin.models.schedule.FixedTTL"
            },
            "class_": "feeds_admin.models.schedule.Weekly",
            "starts": [
                {
                    "day": 0,
                    "time": {
                        "value": "16:11:00+00:00",
                        "class_": "datetime.time"
                    },
                    "class_": "feeds_admin.models.schedule.DayOfWeek"
                }
            ],
            "start_at": {
                "value": "2018-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2022-06-22T19:10:25-07:00",
                "class_": "datetime.datetime"
            }
        }'
    );


INSERT INTO feeds_admin.feeds
    (
        target_service,
        feed_uuid,
        schedule_id,
        payload,
        status,
        author
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
        'publishing',
        'adomogashev'
    ),
    (  -- Yeah, it's incorrect state: publishing => weekly.
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
        'publishing',
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
        'created',
        'adomogashev'
    ),
    (
        'driver_wall',
        '44444444444444444444444444444444',
        4,
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
    )
;
