INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "all"}'::jsonb
    ),
    (
        '22222222222222222222222222222222',
        20,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "brand"}'::jsonb
    ),
    (
        '33333333333333333333333333333333',
        30,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "city"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('100', 20),
    ('moscow', 30);

INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
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
        1,
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
    ),
    (
        'eats-restaurants-notification',
        '22222222222222222222222222222222',
        1,
        'RestApp',
        '{}'::jsonb,
        '{
            "info": {
                "important": false,
                "priority": 101,
                "show_as_fullscreen": false
            },
            "preview": {"title": "Заголовок"},
            "content": {
                "text": "Основной текст нотификации с Markdown",
                "media_id": "3f30427b198b4d56be1aecaf73c83597"
            }
        }'::jsonb,
        'created',
        'v-belikov',
        'TAXICRM-1',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    ),
    (
        'eats-restaurants-survey',
        '33333333333333333333333333333333',
        1,
        'RestApp',
        '{}'::jsonb,
        '{
          "info": {
            "important": false,
            "priority": 101,
            "show_as_fullscreen": false
          },
          "preview": {
            "title": "Заголовок",
            "button": {
              "text": "Текст на кнопке"
            }
          },
          "content": {
            "content_type": "story",
            "pages": [
              {
                "question": "Вопрос 1",
                "description": "Описание",
                "answer": {
                  "type": "single",
                  "answers": [
                    {
                      "type": "predefined",
                      "text": "Вариант ответа 1"
                    },
                    {
                      "type": "predefined",
                      "text": "Вариант ответа 2"
                    },
                    {
                      "type": "other",
                      "text": "Другое"
                    }
                  ],
                  "url": "https://yandex.ru"
                }
              },
              {
                "question": "Вопрос 2",
                "description": "От этого вопроса зависит следующий",
                "answer": {
                  "type": "single",
                  "answers": [
                    {
                      "type": "predefined",
                      "text": "Вариант ответа 1"
                    },
                    {
                      "type": "predefined",
                      "text": "Вариант ответа 2"
                    },
                    {
                      "type": "other",
                      "text": "Другое"
                    }
                  ],
                  "url": "https://yandex.ru"
                }
              },
              {
                "question": "Вопрос 3",
                "description": "Расскажите почему вы выбрали вариант ''Другое''",
                "answer": {
                  "type": "text",
                  "dependencies": [
                    {
                      "answer_index": 1,
                      "answers": [
                        2
                      ]
                    }
                  ]
                }
              },
              {
                "question": "Вопрос 4",
                "description": "Описание",
                "answer": {
                  "type": "rating",
                  "max_rating": 5,
                  "url": "https://yandex.ru"
                }
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
