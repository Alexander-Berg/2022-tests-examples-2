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
    ('Moscow', 2),
    ('Novosibirsk', 2),
    ('Moscow', 3),
    ('Novosibirsk', 3),
    ('Moscow', 4),
    ('Novosibirsk', 4);

INSERT INTO feeds_admin.feeds
    (
        feed_uuid,
        target_service,
        name,
        settings,
        payload,
        status,
        schedule_id,
        author,
        ticket,
        created,
        updated
    )
VALUES
    (
        '11111111111111111111111111111111',
        'driver_wall',
        'DriverWall',
        '{
            "application": "taximeter",
            "use_wave_sending": false,
            "crm_campaign_id": "hex"
        }'::jsonb,
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
        NULL,
        'v-belikov',
        'TAXICRM-1',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    ),
    (
        '22222222222222222222222222222222',
        'driver_wall',
        'DriverWall',
        '{
            "application": "taximeter",
            "use_wave_sending": false
        }'::jsonb,
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
        NULL,
        'v-belikov',
        'TAXICRM-1',
        '2020-12-30 00:00:00+0300'::timestamp with time zone,
        '2020-12-31 00:00:00+0300'::timestamp with time zone
    ),
    (
        '33333333333333333333333333333333',
        'driver_wall',
        'DriverWall',
        '{
            "application": "taximeter",
            "use_wave_sending": false,
            "crm_campaign_id": "hex"
        }'::jsonb,
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
        NULL,
        'v-belikov',
        'TAXICRM-1',
        '2021-12-30 00:00:00+0300'::timestamp with time zone,
        '2021-12-31 00:00:00+0300'::timestamp with time zone
    ),
    (
        '44444444444444444444444444444444',
        'driver_wall',
        'DriverWall',
        '{
            "application": "taximeter",
            "use_wave_sending": false,
            "crm_campaign_id": "hex"
        }'::jsonb,
        '{
            "title": "Заголовок",
            "text": "Текст **markdown** с {параметрами}",
            "url": "https://yandex.ru",
            "teaser": "Текст на ссылке",
            "type": "survey",
            "dom_storage": true,
            "notification_mode": "normal",
            "important": false,
            "alert": true,
            "format": "Markdown",
            "url_open_mode": "browser"
        }'::jsonb,
        'publishing',
        NULL,
        'v-belikov',
        'TAXICRM-1',
        '2021-12-30 00:00:00+0300'::timestamp with time zone,
        '2021-12-31 00:00:00+0300'::timestamp with time zone
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, run_id, planned_start_at, finished_at, status, recipient_count, error_reason, message
    )
VALUES
    (
        '11111111111111111111111111111111',
        1,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        'success',
        2,
        NULL,
        NULL
    ),
    (
        '33333333333333333333333333333333',
        3,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        NULL,
        'in_progress',
        2,
        NULL,
        NULL
    );
