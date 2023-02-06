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
        NULL,
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    );
