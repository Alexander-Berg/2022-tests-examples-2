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
     'id1',
     null,
     null,
     'banner 1',
     to_tsvector('banner 1'),
     'fullscreen',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag1', 'tag2']::TEXT[],
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
                        {
                            "color": "feafea",
                            "text": "action button",
                            "text_color": "ffffff",
                            "deeplink": "deeplink"
                        },
                        {
                            "color": "feafea",
                            "text": "action button",
                            "text_color": "ffffff",
                            "action": {
                                "type": "web_view",
                                "payload": {
                                    "content": "deeplink"
                                }
                            }
                        }
                    ]
                }
            }
       ]}'
     )::jsonb,
     ('{
            "is_attributed_text": true,
            "overlays": [{"text": "overlay_value"}]
        }'
     )::jsonb
),
(
     'id2',
     null,
     null,
     'banner 12',
     to_tsvector('banner 12'),
     'fullscreen',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag3', 'tag4']::TEXT[],
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
     'id3',
     null,
     null,
     'banner 3',
     to_tsvector('banner 3'),
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
     'promotions_test_publish',
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
     'revision',
     ('{
         "data": [
             {
                 "revision": "some_revision1",
                 "created_at": "2019-07-22T16:51:09+0000"
             },
             {
                 "revision": "some_revision2",
                 "created_at": "2019-07-22T16:51:10+0000"
             },
             {
                 "revision": "some_revision3",
                 "created_at": "2019-07-22T16:51:11+0000"
             },
             {
                 "revision": "some_revision4",
                 "created_at": "2019-07-22T16:51:12+0000"
             },
             {
                 "revision": "some_revision5",
                 "created_at": "2019-07-22T16:51:13+0000"
             }
         ]
     }')::jsonb,
     'banner 4',
     to_tsvector('banner 4'),
     'notification',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['tag7', 'tag8']::TEXT[],
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
     'id5',
     null,
     null,
     'banner 5',
     to_tsvector('banner 5'),
     'fullscreen',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag9', 'tag10']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     null,
     null,
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
                        {
                            "color": "feafea",
                            "text": "action button",
                            "text_color": "ffffff",
                            "deeplink": "deeplink"
                        },
                        {
                            "color": "feafea",
                            "text": "action button",
                            "text_color": "ffffff",
                            "action": {
                                "type": "web_view",
                                "payload": {
                                    "content": "deeplink"
                                }
                            }
                        }
                    ]
                }
            }
       ]}'
     )::jsonb,
     ('{
            "is_attributed_text": true,
            "overlays": [{"text": "overlay_value"}],
            "campaign_labels": ["campaign1"]
        }'
     )::jsonb
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
            "campaign_labels": ["campaign1"]
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
     ARRAY['main']::TEXT[],
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
            "campaign_labels": ["campaign1"]
        }'
     )::jsonb
),
(
     '6b2ee5529f5b4ffc8fea7008e6913ca6',
     null,
     null,
     '12',
     to_tsvector('12'),
     'notification',
     '2019-10-04 07:39:09.140720 +00:00',
     '2019-10-04 07:39:09.140720 +00:00',
     null,
     'created',
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
     null
),
(
     'story_id1',
     null,
     null,
    'story 1',
     to_tsvector('story 1'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['tag77', 'tag88']::TEXT[],
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
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"},
                        {"color": "feafea", "text": "action button", "text_color": "ffffff",
                         "action": {"payload": {"content": "", "need_authorization": false}, "type": "screenshare"}}
                    ]
                },
                "layout": {"id": "layout_id"}
            }
       ]}'
     )::jsonb,
     ('{
         "mark_read_after_tap": true,
         "is_tapable": true,
         "min_pages_amount": 4,
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         }
     }')::jsonb
),
(
     'story_id2',
     null,
     null,
    'story 2',
     to_tsvector('story 2'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'created',
     ARRAY['tag77', 'tag88']::TEXT[],
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
         "meta_type": "old_story",
         "story_context": "totw",
         "mark_read_after_tap": true,
         "is_tapable": true,
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         }
     }')::jsonb
),
(
     'deeplink_shortcut_id1',
     null,
     null,
    'deeplink_shortcut 1',
     to_tsvector('deeplink_shortcut 1'),
     'deeplink_shortcut',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['tag77', 'tag88']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     null,
     null,
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
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         },
         "action": {
             "action_type": "deeplink",
             "content": "content"
         },
         "meta_type": "meta_type"
     }')::jsonb
),
(
     'deeplink_shortcut_id2',
     null,
     null,
    'deeplink_shortcut 2',
     to_tsvector('deeplink_shortcut 2'),
     'deeplink_shortcut',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['tag77', 'tag88']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     null,
     null,
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
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         },
         "action": {
             "action_type": "deeplink",
             "content": "content"
         },
         "meta_type": "meta_type"
     }')::jsonb
),
(
     'eda_unpublished',
     'revision',
     ('{
         "data": [
             {
                 "revision": "some_revision1",
                 "created_at": "2019-07-22T16:51:09+0000"
             },
             {
                 "revision": "some_revision2",
                 "created_at": "2019-07-22T16:51:10+0000"
             },
             {
                 "revision": "some_revision3",
                 "created_at": "2019-07-22T16:51:11+0000"
             },
             {
                 "revision": "some_revision4",
                 "created_at": "2019-07-22T16:51:12+0000"
             },
             {
                 "revision": "some_revision5",
                 "created_at": "2019-07-22T16:51:13+0000"
             }
         ]
     }')::jsonb,
     'eda_banner_unpublished',
     to_tsvector('eda_banner_unpublished'),
     'eda_banner',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'eda_exp',
     false,
     null,
     ('{"pages": [
        {
          "images": [
            {
              "url": "https://eda.yandex/light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ]
        }
       ]}'
     )::jsonb,
     ('{
         "banner_type": "info",
         "app_url": "https://ya.ru/mobile",
         "url": "https://ya.ru",
         "geojson": [[37.58079528808594, 55.91458189198758], [37.49290466308594, 55.90034110284034], [37.3919677734375, 55.870688097921345]],
          "region_id": "123",
          "brand_id": "2",
          "place_id": "9",
          "collection_slug": "http://ya.ru"
       }
     ')::jsonb
),
(
     'eda_published',
     'revision',
     ('{
         "data": [
             {
                 "revision": "some_revision",
                 "created_at": "2019-07-22T16:51:09+0000"
             }
         ]
     }')::jsonb,
     'eda_banner_published',
     to_tsvector('eda_banner_published'),
     'eda_banner',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'eda_exp',
     false,
     null,
     ('{"pages": [
        {
          "images": [
            {
              "url": "https://eda.yandex/light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ]
        }
       ]}'
     )::jsonb,
     null
),
(
    'promo_on_summary1',
    NULL,
    NULL,
    'express',
    to_tsvector('express'),
    'promo_on_summary',
    '2020-09-07 16:53:50.235707',
    '2020-09-07 16:53:50.235707',
    '2020-09-07 16:53:50.235707',
    'published',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['summary']::TEXT[],
    1,
    '2020-09-07 16:53:50.235707',
    '2020-10-01 00:00:00.000000',
    'promo_on_summary_delivery',
    false,
    NULL,
    ('
        {
            "pages": [
                {
                    "title": {
                        "items": [
                            {
                                "text": "promo_on_summary.delivery.title",
                                "type": "text",
                                "is_tanker_key": true
                            }
                        ]
                    },
                    "widgets": {
                        "deeplink_arrow_button": {
                            "color": "000000",
                            "items": [
                                {
                                    "type": "image",
                                    "image_tag": "class_express_icon_7"
                                }
                            ],
                            "deeplink": "yandextaxi://route?tariffClass=express"
                        }
                    }
                }
            ]
        }
    ')::jsonb,
    ('
        {
            "meta_type": "promo_block",
            "show_policy": {
                "max_show_count": 10,
                "max_widget_usage_count": 3
            },
            "supported_classes": ["econom", "comfort", "comfortplus", "vip"],
            "feeds_admin_id": "11123"
        }
    ')::jsonb
),
(
    'totw_banner_1', -- id
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
            "show_policy": {
                "id": "show_policy_id",
                "max_show_count": 5,
                "max_widget_usage_count": 1
            }
        }
    ')::jsonb -- extra_fields
),
(
    'object_over_map_1', -- id
    NULL, -- revision
    NULL, -- revision_history
    'object_over_map_name', -- name
    to_tsvector('object_over_map_name'), -- name_tsv
    'object_over_map', -- promotion_type
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
    'object_over_map_exp', -- experiment
    false, -- has_yql_data
    NULL, -- yql_data
    ('
        {
            "pages": []
        }
    ')::jsonb, -- pages
    ('
        {
            "accessibility_text": {
                "text": "accessibility_text_key",
                "is_tanker_key": true
            },
            "action": {
                "deeplink": "yandextaxi://",
                "type": "deeplink"
            },
            "bubble": {
                "attr_text": "key",
                "is_tanker_key": true
            },
            "content": {
                "animation_count": 3,
                "delay": 0.3,
                "source": {
                    "type": "remote",
                    "url": "https://mds.yandex.ru/"
                },
                "tap_count": 1,
                "type": "animation"
            },
            "position": "center_start",
            "show_policy": {
                "id": "show_policy_id",
                "max_show_count": 5,
                "max_usage_count": 1
            }
        }
    ')::jsonb -- extra_fields
),
(
     'grocery_unpublished', -- id
     null, -- revision
     null, -- revision_history
     'grocery_informer_unpublished', --name
     to_tsvector('grocery_informer_unpublished'), -- name_tsv
     'grocery_informer', -- promotion_type
     '2019-07-22T16:51:09+0000', -- created_at
     '2019-07-22T16:51:09+0000', -- updated_at
     null, -- published_at
     'archived', -- status
     null, -- meta_tags
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
         }
     }
     ')::jsonb -- extra_fields
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
