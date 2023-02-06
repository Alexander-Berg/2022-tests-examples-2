INSERT INTO promotions.promotions (
    id,
    revision,
    revision_history,
    name,
    name_tsv,
    promotion_type,
    created_at,
    updated_at,
    published_at,
    status,
    meta_tags,
    zones,
    screens,
    priority,
    starts_at,
    ends_at,
    experiment,
    has_yql_data,
    yql_data,
    pages,
    extra_fields) VALUES
(
    'totw_banner_1',
    NULL,
    NULL,
    'totw_banner_name_1', 
    to_tsvector('totw_banner_name_1'),
    'totw_banner',
    '2020-09-07T16:53:50.235707Z',
    '2020-09-07T16:53:50.235707Z',
    '2020-09-07T16:53:50.235707Z',
    'published',
    NULL,
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    5,
    '2020-09-07T16:53:50.235707Z',
    '2020-10-01T00:00:00.000000Z',
    'totw_banner_exp',
    false,
    NULL,
    ('
        {
            "pages": [
                {
                    "title": {
                        "content": "totw_banner.title",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "text": {
                        "content": "totw_banner.text",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "icon": {
                        "image_tag": "icon_image_tag",
                        "image_url": "http://image_url"
                    },
                    "backgrounds": [
                        {
                            "type": "image",
                            "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png"
                        }
                    ],
                    "widgets": {
                        "action_buttons": [
                            {
                                "color": "AAAAAA",
                                "text": "",
                                "text_color": "FFFFFF",
                                "deeplink": "yandextaxi://banner"
                            }
                        ]
                    }
                }
            ]
        }
    ')::jsonb,
    ('
        {
            "campaign_labels": [
                "test_campaign_label_1",
                "test_campaign_label_2"
            ]
        }
    ')::jsonb
),
(
    'totw_banner_2', -- id
    NULL, -- revision
    NULL, -- revision_history
    'totw_banner_name', -- name
    to_tsvector('totw_banner_name'), -- name_tsv
    'totw_banner', -- promotion_type
    '2020-09-07T16:53:50.235707Z', -- created_at
    '2020-09-07T16:53:50.235707Z', -- updated_at
    '2020-09-07T16:53:50.235707Z', -- published_at
    'published', -- status
    NULL, -- meta_tags
    ARRAY[]::TEXT[], -- zones
    ARRAY[]::TEXT[], -- screens
    5, -- priority
    '2020-09-07T16:53:50.235707Z', -- starts_at
    '2020-10-01T00:00:00.000000Z', -- ends_at
    'totw_banner_exp', -- experiment
    false, -- has_yql_data
    NULL, -- yql_data
    ('
        {
            "pages": [
                {
                    "title": {
                        "content": "totw_banner.title",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "text": {
                        "content": "totw_banner.text",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "icon": {
                        "image_tag": "icon_image_tag",
                        "image_url": "http://image_url"
                    },
                    "backgrounds": [
                        {
                            "type": "image",
                            "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png"
                        }
                    ],
                    "widgets": {
                        "action_buttons": [
                            {
                                "color": "AAAAAA",
                                "text": "",
                                "text_color": "FFFFFF",
                                "deeplink": "yandextaxi://banner"
                            }
                        ]
                    }
                }
            ]
        }
    ')::jsonb, -- pages
    ('
        {
            "campaign_labels": [
                "test_campaign_label_3"
            ]
        }
    ')::jsonb -- extra_fields
),
(
    'totw_banner_3', -- id
    NULL, -- revision
    NULL, -- revision_history
    'totw_banner_name_3', -- name
    to_tsvector('totw_banner_name_3'), -- name_tsv
    'totw_banner', -- promotion_type
    '2020-09-07T16:53:50.235707Z', -- created_at
    '2020-09-07T16:53:50.235707Z', -- updated_at
    '2020-09-07T16:53:50.235707Z', -- published_at
    'published', -- status
    NULL, -- meta_tags
    ARRAY[]::TEXT[], -- zones
    ARRAY[]::TEXT[], -- screens
    5, -- priority
    '2020-09-07T16:53:50.235707Z', -- starts_at
    '2020-10-01T00:00:00.000000Z', -- ends_at
    NULL, -- experiment
    false, -- has_yql_data
    NULL, -- yql_data
    ('
        {
            "pages": [
                {
                    "title": {
                        "content": "totw_banner.title",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "text": {
                        "content": "totw_banner.text",
                        "color": "AAAAAA",
                        "is_tanker_key": true
                    },
                    "icon": {
                        "image_tag": "icon_image_tag",
                        "image_url": "http://image_url"
                    },
                    "backgrounds": [
                        {
                            "type": "image",
                            "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png"
                        }
                    ],
                    "widgets": {
                        "action_buttons": [
                            {
                                "color": "AAAAAA",
                                "text": "",
                                "text_color": "FFFFFF",
                                "deeplink": "yandextaxi://banner"
                            }
                        ]
                    }
                }
            ]
        }
    ')::jsonb, -- pages
    ('
        {
            "campaign_labels": [
                "test_campaign_label_4"
            ]
        }
    ')::jsonb -- extra_fields
),
(
     'card_2',
     null,
     null,
     'banner card 2',
     to_tsvector('banner card 2'),
     'card',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag5', 'tag6']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     null,
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
     ('{
            "campaign_labels": ["test_campaign_label_1"]
        }'
     )::jsonb
),
(
     'notification_3',
     null,
     null,
     'banner notification 3',
     to_tsvector('banner notification 3'),
     'notification',
     '2019-10-04 07:39:09.140720 +00:00',
     '2019-10-04 07:39:09.140720 +00:00',
     null,
     'published',
     ARRAY['tag9', 'tag10']::TEXT[],
     ARRAY[]::TEXT[],
     ARRAY['23']::TEXT[],
     23,
     null,
     null,
     null,
     false,
     null,
     ('{"pages": [
         {
             "text": {"color": "1", "content": "1"},
             "title": {"color": "1", "content": "1"},
             "widgets": {
                 "action_buttons": [
                     {"text": "1", "color": "1", "text_color": "1"}
                 ]
             },
             "alt_title": {"color": "1", "content": "1"}
         }
       ]}')::jsonb,
     ('{
            "campaign_labels": ["test_campaign_label_1"]
        }'
     )::jsonb
),
(
     'grocery_published', -- id
     null, -- revision
     null, -- revision_history
     'grocery_informer_published', --name
     to_tsvector('grocery_informer_published'), -- name_tsv
     'grocery_informer', -- promotion_type
     '2019-07-22T16:51:09+0000', -- created_at
     '2019-07-22T16:51:09+0000', -- updated_at
     null, -- published_at
     'published', -- status
     null, -- meta_tags
     ARRAY[]::TEXT[], -- zones
     ARRAY[]::TEXT[], -- screens
     1, -- priority
     '2019-05-22T16:51:09+0000', -- starts_at
     '2022-07-22T16:51:09+0000', -- ends_at
     null, -- experiment
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
                            "color": "#AAAAAA",
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
         "campaign_labels": ["test_campaign_label_1"]
     }
     ')::jsonb -- extra_fields
);
