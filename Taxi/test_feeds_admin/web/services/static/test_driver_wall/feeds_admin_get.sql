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
        '22222222222222222222222222222222',
        20,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 10),
    ('Novosibirsk', 10),
    ('Moscow', 20),
    ('Novosibirsk', 20);

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
            "url_open_mode": "browser",
            "image_id": "image_id"
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
            "url_open_mode": "browser",
            "image_id": "image_id"
        }'::jsonb,
        'created',
        NULL,
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
    ),
    (
        '22222222222222222222222222222222',
        20,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        NULL,
        'in_progress',
        2,
        NULL,
        NULL
    );
