INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        1,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{
            "includes_pages": ["main", "news"],
            "parks": ["dbid1", "dbid2"],
            "cities": ["Moscow", "Novosibirsk"],
            "countries": ["Russia"],
            "excludes_pages": ["removed"],
            "test_parks": ["test_dbid1", "test_dbid2"],
            "positions": ["director"]
         }'::jsonb
    );

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
    );

INSERT INTO feeds_admin.feeds
    (
        target_service,
        feed_uuid,
        schedule_id,
        settings,
        payload,
        status,
        author
    )
VALUES
    (
        'fleet-fullscreens',
        '11111111111111111111111111111111',
        1,
        '{}'::jsonb,
        '{
            "content": {
                "title": "Заголовок фулскрина",
                "pages": [
                    {
                        "text": "Текст на слайде 1",
                        "uuid": "154afb61-3eab-4be9-b1ff-06e1cdeea02b",
                        "widgets": [
                            {
                                "link": "https://ya.ru",
                                "text": "Yandex",
                                "type": "link",
                                "color": "FCE000"
                            },
                            {
                                "link": "",
                                "type": "next_slide",
                                "color": ""
                            },
                            {
                                "link": "",
                                "type": "close",
                                "color": ""
                            }
                        ]
                    },
                    {
                        "text": {
                            "key": "fleet_key",
                            "keyset": "fleet_keyset"
                        },
                        "uuid": "8d3bca48-05ed-4171-900c-08109a309582",
                        "widgets": [
                            {
                                "link": "https://ya.ru/link",
                                "text": "Текст ссылки",
                                "type": "link",
                                "color": "F1F0ED"
                            }
                        ]
                    }
                ]
            },
            "options": {
                "state": "production",
                "priority": 2,
                "execution_rules": [
                    "new_users_only"
                ]
            }
        }'::jsonb,
        'created',
        'adomogashev'
    );

INSERT INTO feeds_admin.run_history
    (
        feed_uuid, started_at, finished_at, status, error_reason, message
    )
VALUES
    (
        '11111111111111111111111111111111',
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        '2018-06-22 19:11:25-07'::timestamp with time zone,
        'success',
        NULL,
        NULL
    );
