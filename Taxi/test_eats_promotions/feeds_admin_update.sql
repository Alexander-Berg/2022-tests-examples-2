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
        'eats-promotions-story',
        '11111111111111111111111111111111',
        10,
        'Eats Story',
        '{
            "experiment": "my_experiment"
         }'::jsonb,
        '{
            "priority": 101,
            "screens": [
                "main",
                "payment"
            ],
            "groups": [
                "group1",
                "group2"
            ],
            "is_tapable": true,
            "mark_read_after_tap": true,
            "preview": {
                "text": {
                    "color": "FFFFFF",
                    "content": "Недели Италии"
                },
                "title": {
                    "color": "FFFFFF",
                    "content": {
                        "keyset": "eda_client",
                        "key": "translate_me"
                    }
                },
                "backgrounds": [
                    {
                        "type": "image",
                        "media_id": "3f30427b198b4d56be1aecaf73c83597"
                    },
                    {
                        "type": "color",
                        "content": "6D131C"
                    }
                ]
            },
            "pages": [
                {
                    "autonext": true,
                    "duration": 15,
                    "text": {
                        "color": "FCE381",
                        "content": "text"
                    },
                    "title": {
                        "color": "FFCF6A",
                        "content": "header"
                    },
                    "backgrounds": [
                        {
                            "type": "color",
                            "content": "FFCF6A"
                        },
                        {
                            "type": "image",
                            "media_id": "3f30427b198b4d56be1aecaf73c83597"
                        }
                    ],
                    "widgets": {
                        "close_button": {
                            "color": "21201F"
                        },
                        "pager": {
                            "color_on": "FFCF6A",
                            "color_off": "EA503F"
                        },
                        "menu_button": {
                            "color": "FFCF6A"
                        },
                        "link": {
                            "text": "Текст ссылки",
                            "action": {
                                "type": "deeplink",
                                "payload": {
                                    "content": "https://google.com",
                                    "need_authorization": true
                                }
                            },
                            "text_color": "FFCF6A"
                        },
                        "action_buttons": [
                            {
                                "text": "Кнопки с диплинком",
                                "color": "FFCF6A",
                                "text_color": "FFCF6A",
                                "action": {
                                    "type": "deeplink",
                                    "payload": {
                                        "content": "https://yandex.ru",
                                        "need_authorization": true
                                    }
                                }
                            },
                            {
                                "text": "Кнопка перехода на i-ую страницу",
                                "text_color": "FFCF6A",
                                "color": "FFCF6A",
                                "action": {
                                    "type": "move",
                                    "payload": {
                                        "page": "3",
                                        "need_authorization": true
                                    }
                                }
                            },
                            {
                                "text": "Кнопка поделиться",
                                "text_color": "FFCF6A",
                                "color": "FFCF6A",
                                "action": {
                                    "type": "share",
                                    "payload": {
                                        "content": "https://yandex.ru",
                                        "need_authorization": true
                                    }
                                }
                            },
                            {
                                "text": "Кнопка, открывающая web view",
                                "text_color": "EBAE41",
                                "color": "FFCF6A",
                                "action": {
                                    "type": "web_view",
                                    "payload": {
                                        "content": "https://yandex.ru",
                                        "need_authorization": true
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "autonext": false,
                    "duration": 5,
                    "text": {
                        "color": "FCE381",
                        "content": "text"
                    },
                    "title": {
                        "color": "FFCF6A",
                        "content": "header"
                    },
                    "backgrounds": [
                        {
                            "type": "color",
                            "content": "FFCF6A"
                        }
                    ],
                    "widgets": {
                        "close_button": {
                            "color": "21201F"
                        },
                        "pager": {
                            "color_on": "FFCF6A",
                            "color_off": "EA503F"
                        }
                    }
                }
            ]
        }'::jsonb,
        'created',
        'v-belikov',
        'TAXICRM-1234',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    );
