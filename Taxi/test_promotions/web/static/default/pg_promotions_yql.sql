INSERT INTO promotions.promotions (
    id,
    name,
    name_tsv,
    promotion_type,
    created_at,
    updated_at,
    published_at,
    status,
    zones,
    screens,
    priority,
    starts_at,
    ends_at,
    experiment,
    has_yql_data,
    yql_data,
    pages) VALUES
(
    '7f2179daaa4a4e86b2675334dd27b842',  -- id
    '1 2 3 yql',  -- name
    to_tsvector('1 2 3 yql'),  -- name_tsv
    'notification',  -- promotion_type
    '2019-11-20 11:14:56.249415 +00:00',  -- created_at
    '2019-11-20 11:14:56.249415 +00:00',  -- updated_at
    '2019-11-20 11:16:01.092144 +00:00',  -- published_at
    'published',  -- status
    ARRAY[]::TEXT[],  -- zones
    ARRAY['menu']::TEXT[],  -- screen
    1,  -- priority
    '2019-05-22T16:51:09+0000',  -- starts_at
    '2022-07-22T16:51:09+0000',  -- ends_at
    '1',  -- experiment
    true,  -- has_yql_data
    ('{"link": "https://yql.yandex-team.ru/Operations/XdVKKp3uduyEeBbdw-cIybBhMhCiK6sSFat29eO3hfQ="}')::jsonb,  -- yql_data
    ('{
        "pages": [
            {
                "text": {"color": "0C1E40", "content": "Last city - {attr_city}. Last price - {order_price}"},
                "title": {"color": "0C1E40", "content": "Hello, {yandex_uid}"},
                "widgets": {
                    "arrow_button": {"color": "010102", "deeplink": "https://yandex.ru"},
                    "action_buttons": [
                        {"text": "{order_price} OK", "color": "1", "text_color": "1"}
                    ]
                }
            }
        ]
    }')::jsonb),  -- pages
    (
        'a4f5087f30954ee486ed7e5b21bbc35e',
        'yql test',
        to_tsvector('yql test'),
        'notification',
        '2019-11-15 09:24:39.789669 +00:00',
        '2019-11-15 09:24:39.789669 +00:00',
        '2019-11-18 16:52:42.290372 +00:00',
        'published',
        ARRAY[]::TEXT[],
        ARRAY['main']::TEXT[],
        12,
        '2019-11-22 16:51:09.000000 +00:00',
        '2019-11-26 16:51:09.000000 +00:00',
        '123',
        true,
        ('{"link": "https://yql.yandex-team.ru/Operations/XckhK53udvyn7AFYeYLM94LFzdvVTT3MDfkZXvGd_us=?editor_page=main"}')::jsonb,
        ('{
            "pages": [
                {
                    "text": {"color": "010102", "content": "your last ride was in {attr_city} and costed {order_price}"},
                    "title": {"color": "010102", "content": "hello, {yandex_uid}!"},
                    "widgets": {"action_buttons": []}
                }
            ]
        }')::jsonb),
    (
        'e8917b72eb694b6ca94bdfabf7a14caa',
        '123123123',
        to_tsvector('123123123'),
        'fullscreen',
        '2019-10-11 13:14:14.544308',
        '2019-10-11 13:14:14.544308',
        null,
        'published',
        ARRAY[]::TEXT[],
        ARRAY['123']::TEXT[],
        1,
        '2019-03-22T16:51:09+0000',
        '2022-07-22T16:51:09+0000',
        'okok',
        true,
        ('{
            "link": "https://yql.yandex-team.ru/Operations/XckhK53udvyn7AFYeYLM94LFzdvVTT3MDfkZXvGd_us=?editor_page=main",
            "retries": 3
          }'
        )::jsonb,
        ('{
            "pages": [
                {
                    "title": {"color": "010102", "content": "{absent_key}"},
                    "widgets": {
                        "close_button": {"color": "FFFFFF"},
                        "action_buttons": []
                    }
                }
            ]
        }')::jsonb),
    (
        '6b2ee5529f5b4ffc8fea7008e6913ca7',
        '12',
        to_tsvector('12'),
        'notification',
        '2019-10-04 07:39:09.140720 +00:00',
        '2019-10-04 07:39:09.140720 +00:00',
        null,
        'publishing',
        ARRAY[]::TEXT[],
        ARRAY['23']::TEXT[],
        23,
        '2019-05-22T16:51:09+0000',
        '2022-07-22T16:51:09+0000',
        'exp_fs',
        true,
        ('{"link": "https://localhost/Operations/yql_query_id"}')::jsonb,
        ('{"pages": [
            {
            "text": {"color": "1", "content": "{content_1}"},
            "title": {"color": "1", "content": "{content_2}"},
            "widgets": {
                "action_buttons": [
                    {"text": "1", "color": "1", "text_color": "1"}
                ],
                "link": {"text": "{text_1}", "text_color": "fafafa", "deeplink": "qwe"}
            },
            "alt_title": {"color": "1", "content": "content {content_2} subs"}
        }]}')::jsonb
);
