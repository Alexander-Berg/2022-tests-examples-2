INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "cities"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('Moscow', 10),
    ('Novosibirsk', 10);

INSERT INTO feeds_admin.feeds
    (
        feed_uuid,
        target_service,
        name,
        settings,
        payload,
        status,
        author,
        ticket,
        created,
        updated,
        schedule_id
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
        'v-belikov',
        'TAXICRM-1',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone,
        NULL
    );
