INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "all"}'::jsonb
    );

INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        10,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2020-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "2020-01-10T00:00:00+03:00",
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
        ticket,
        created,
        updated
    )
VALUES
    (
        'eats-restaurants-news',
        '11111111111111111111111111111111',
        10,
        'RestApp',
        '{}'::jsonb,
        '{
            "info": {
                "topic": "tutorial",
                "important": true,
                "priority": 101,
                "show_as_fullscreen": false,
                "url": "https://yandex.ru",
                "url_title": "Название ссылки"
            },
            "preview": {
                "title": "Заголовок",
                "media_id": "3f30427b198b4d56be1aecaf73c83597"
            },
            "widget": {
                "title": "Заголовок",
                "url": "https://yandex.ru",
                "url_title": "Название ссылки",
                "background": {"color": "FFFFFF"},
                "button": {"text": "Текст в кнопке", "color": "FFFFFF"}
            },
            "content": {
                "content_type": "story",
                "pages": [
                    {
                        "text": "Текст слайда 1",
                        "media_id": "3f30427b198b4d56be1aecaf73c83597"
                    },
                    {
                        "text": "Текст слайда 2",
                        "media_id": "some_identifier"
                    }
                ]
            }
        }'::jsonb,
        'created',
        'v-belikov',
        'TAXICRM-1',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, run_id, planned_start_at, finished_at, status, recipient_count, error_reason, message
    )
VALUES
    (
        '11111111111111111111111111111111',
        10,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        'success',
        2,
        NULL,
        NULL
    );
