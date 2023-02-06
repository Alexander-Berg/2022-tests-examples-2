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
    pages,
    extra_fields
) VALUES
(
     'id1',
     'banner 1',
     to_tsvector('banner 1'),
     'fullscreen',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "alt_title": {"content": "alt_title3", "color": "aaeedd"},
                "text": {"content": "text3", "color": "eaeaea"},
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     null
),
(
     'id2',
     'banner 12',
     to_tsvector('banner 12'),
     'fullscreen',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "alt_title": {"content": "alt_title3", "color": "aaeedd"},
                "text": {"content": "text3", "color": "eaeaea"},
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     null
),
(
     'id3',
     'banner 3',
     to_tsvector('banner 3'),
     'card',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "alt_title": {"content": "alt_title3", "color": "aaeedd"},
                "text": {"content": "text3", "color": "eaeaea"},
                "is_foldable": true,
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     null
),
(
     'id4',
     'banner 4',
     to_tsvector('banner 4'),
     'notification',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "text": {"content": "text3", "color": "eaeaea"},
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     null
),
(
     'id42',
     'banner 42',
     to_tsvector('banner 42'),
     'notification',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "text": {"content": "text3", "color": "eaeaea"},
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     null
),
(
     '6b2ee5529f5b4ffc8fea7008e6913ca6',
     '12',
     to_tsvector('12'),
     'notification',
     '2019-10-04 07:39:09.140720 +00:00',
     '2019-10-04 07:39:09.140720 +00:00',
     null,
     'created',
     ARRAY[]::TEXT[],
     ARRAY['23']::TEXT[],
     23,
     null,
     null,
     null,
     false,
     null,
     ('{"pages": [
         {"text": {"color": "1", "content": "1"},
         "title": {"color": "1", "content": "1"},
         "widgets": {
             "action_buttons": [
                 {"text": "1", "color": "1", "text_color": "1"}
             ]
          }
        }]
    }')::jsonb,
    null
),
(
    '8c886014c315495e956da49195d1072e',
    'dasha0',
    to_tsvector('dasha0'),
    'story',
    '2020-02-06 08:16:48.537490 +00:00',
    '2020-02-06 08:16:48.537490 +00:00',
    null,
    'published',
    ARRAY[]::TEXT[],
    ARRAY['main']::TEXT[],
    4,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    null,
    false,
    null,
    ('{
        "pages": [
            {
                "widgets": {
                    "action_buttons": []
                }
            }
        ]
    }')::jsonb,
    ('{"is_tapable": true}')::jsonb
),
(
    '1316003df78d44168c61e80ce4c814bd',
    'Новая история',
    to_tsvector('Новая история'),
    'story',
    '2020-02-17T04:50:47.901626+0000',
    '2020-02-17T04:50:47.901626+0000',
    '2020-02-17T04:55:18.829764+0000',
    'published',
    ARRAY[]::TEXT[],
    ARRAY['main_screen']::TEXT[],
    42,
    '2020-02-01T08:11:00.000000+0000',
    '2020-02-08T19:22:00.000000+0000',
    'my_exp',
    true,
    ('{"some_yql": "data"}')::jsonb,
    ('{
        "pages": [
            {
                "text": {
                    "color": "E7ECF2",
                    "content": "First slide lorem ipsum"
                },
                "title": {
                    "color": "002864",
                    "content": "first.slide.key",
                    "is_tanker_key": true
                },
                "widgets": {
                    "link": {
                        "text": "First slide link text",
                        "action": {
                            "type": "move",
                            "payload": {
                                "page": 2
                            }
                        },
                        "text_color": "00691F"
                    },
                    "pager": {
                        "color_on": "3662B8",
                        "color_off": "237DC6"
                    },
                    "menu_button": {
                        "color": "E14138"
                    },
                    "action_buttons": [
                        {
                            "text": "Action button text",
                            "color": "143264",
                            "action": {
                                "type": "deeplink",
                                "payload": {
                                    "content": "protocol://deeplink",
                                    "need_authorization": true
                                }
                            },
                            "text_color": "ECE2C9"
                        }
                    ]
                },
                "autonext": true,
                "duration": 11
            },
            {
                "text": {
                    "color": "8590A2",
                    "content": "Text and title. Background only with image"
                },
                "title": {
                    "color": "D68F37",
                    "content": "Second slide normal title",
                    "is_tanker_key": false
                },
                "widgets": {
                    "link": {
                        "text": "link.key",
                        "text_color": "820000",
                        "is_tanker_key": true
                    },
                    "action_buttons": [
                        {
                            "text": "action.button.key",
                            "color": "820000",
                            "text_color": "998E76",
                            "is_tanker_key": true
                        }
                    ]
                },
                "duration": 33
            }
        ]
    }')::jsonb,
    ('{
        "preview": {
            "text": {
                "color": "B1AEEB",
                "content": "Lorem ipsum dolor sit amet"
            },
            "title": {
                "color": "FFDE40",
                "content": "preview.title.key",
                "is_tanker_key": true
            }
        },
        "is_tapable": true,
        "mark_read_after_tap": false
    }')::jsonb
),
(
    '5acd82279fc349eb8c7d0fbb90d25fb7',
    'azbuka_eats',
    to_tsvector('azbuka_eats'),
    'eda_banner',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    NULL,
    'published',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    93,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'exp_fs',
    false,
    NULL,
    ('{
        "pages": [
            {
                "images": [
                    {
                        "url": "https://eda.yandex/images/1387779/bc54af81f78d9fe985072912f5b5640c.png",
                        "theme": "light",
                        "platform": "web"
                    }
                ]
            }
        ]
    }')::jsonb,
    ('{
        "brand_id": "24668",
        "banner_id": 3,
        "banner_type": "brand",
        "description": "azbuka_brand"
    }')::jsonb
),
(
    '5acd82279fc349eb8c7d0fbb90d25fb8',
    'azbuka_eats_yql',
    to_tsvector('azbuka_eats_yql'),
    'eda_banner',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    NULL,
    'published',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    93,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'exp_fs',
    true,
    NULL,
    ('{
        "pages": [
            {
                "images": [
                    {
                        "url": "https://eda.yandex/images/1387779/bc54af81f78d9fe985072912f5b5640c.png",
                        "theme": "light",
                        "platform": "web"
                    }
                ]
            }
        ]
    }')::jsonb,
    ('{
        "brand_id": "24668",
        "banner_id": 3,
        "banner_type": "brand",
        "description": "azbuka_brand"
    }')::jsonb
),
(
     'grocery_informer_faraday', -- id
     'grocery_informer_faraday', --name
     to_tsvector('grocery_informer_faraday'), -- name_tsv
     'grocery_informer', -- promotion_type
     '2019-07-22T16:51:09+0000', -- created_at
     '2019-07-22T16:51:09+0000', -- updated_at
     null, -- published_at
     'published', -- status
     ARRAY[]::TEXT[], -- zones
     ARRAY[]::TEXT[], -- screens
     1, -- priority
     '2019-05-22T16:51:09+0000', -- starts_at
     '2022-07-22T16:51:09+0000', -- ends_at
     'grocery_exp', -- experiment
     false, -- has_yql_data
     null, -- yql_data
     ('{
        "pages": [
            {
                "text": {
                    "content": "Informer Text",
                    "color": "#AAAAAA",
                    "is_tanker_key": false
                },
                "backgrounds": [
                    {
                        "type": "",
                        "content": "#777777"
                    }
                ],
                "icon": {
                    "image_url": "some_url.com"
                },
                "widgets": {}
            },
            {
                "title": {
                    "content": "Modal Title",
                    "color": "#AAAAAA",
                    "is_tanker_key": false
                },
                "text": {
                    "content": "Modal Text",
                    "color": "#AAAAAA",
                    "is_tanker_key": false
                },
                "backgrounds": [
                    {
                        "type": "",
                        "content": "#888888"
                    }
                ],
                "widgets": {
                    "action_buttons": [
                        {
                            "action": "close",
                            "color": "#AAAAAA",
                            "deeplink": "deeplink://somewhere",
                            "text": "OK",
                            "text_color": "#FFFFFF"
                        }
                    ]
                },
                "icon": {
                    "image_url": "some_url.com"
                }
            }
        ]
     }'
     )::jsonb, -- pages
     ('{
         "grocery_extra": {
             "additional_text": "More text"
         },
         "use_full_screen": true,
         "grocery_source": "tracking",
         "show_policy": {
             "max_show_count": 10,
             "max_widget_usage_count": 10,
             "same_priority_order": 1
         },
         "campaign_labels": ["abc", "def"]
     }
     ')::jsonb -- extra_fields
);
