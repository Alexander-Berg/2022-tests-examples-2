INSERT INTO promotions.promotions (
    id,
    name,
    name_tsv,
    promotion_type,
    created_at,
    updated_at,
    published_at,
    status,
    consumers,
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
     'story_id111',
     'story 2',
     to_tsvector('story 2'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     null,
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
         "min_pages_amount": 5,
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         },
         "meta_type": "meta_type",
         "is_attributed_text": true
     }')::jsonb
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
     null,
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
     ('{
          "is_attributed_text": true
       }'
     )::jsonb
),
(
     'id2.2',
     'banner 12.2',
     to_tsvector('banner 12.2'),
     'fullscreen',
     '2010-07-22T16:51:09+0000',
     '2010-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY[]::TEXT[],
     ARRAY['tag3', 'tag4']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2010-05-22T16:51:09+0000',
     '2011-07-22T16:51:09+0000',
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
     'banner 3',
     to_tsvector('banner 3'),
     'card',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['consumer1', 'consumer2']::TEXT[],
     ARRAY['tag5', 'tag6']::TEXT[],
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
     ('{
          "is_attributed_text": true
       }'
     )::jsonb
),
(
     'expired_card_id',
     'expired_card_name',
     to_tsvector('expired_card_name'),
     'card',
     '2018-07-22T16:51:09+0000',
     '2018-07-22T16:51:09+0000',
     null,
     'published',
     null,
     ARRAY['tag5', 'tag6']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2018-05-22T16:51:09+0000',
     '2019-07-22T16:51:00+0000',
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
     ARRAY['consumer1', 'my_consumer']::TEXT[],
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
     '6b2ee5529f5b4ffc8fea7008e6913ca6',
     '12',
     to_tsvector('12'),
     'notification',
     '2019-10-04 07:39:09.140720 +00:00',
     '2019-10-04 07:39:09.140720 +00:00',
     null,
     'created',
     ARRAY['my_consumer', 'consumer2']::TEXT[],
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
     'published_notification_id',
     'published_notification_name',
     to_tsvector('published_notification_name'),
     'notification',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     '2020-02-17T04:55:18+0000',
     'published',
     ARRAY[]::TEXT[],
     ARRAY['tag9', 'tag10']::TEXT[],
     ARRAY['moscow','abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     23,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'exp_fs',
     false,
     null,
     ('{"pages": [
         {
             "text": {"color": "eaeaea", "content": "text3"},
             "title": {"color": "ff00ee", "content": "title3", "type": "large"},
             "widgets": {
                 "action_buttons": [
                     {
                         "color": "feafea",
                         "deeplink": "deeplink",
                         "text": "action button",
                         "text_color": "ffffff"
                     }
                 ],
                 "close_button": {
                     "color": "fefefe"
                 },
                 "menu_button": {
                     "color": "fafafa"
                 },
                 "pager": {
                     "color_off": "ff0011",
                     "color_on": "affafe"
                 }
             }
         }
     ]}')::jsonb,
     ('{
          "is_attributed_text": true
       }'
     )::jsonb
),
(
     'story_id1',
     'story 1',
     to_tsvector('story 1'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     null,
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
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"}
                    ]
                }
            }
       ]}'
     )::jsonb,
     ('{
         "mark_read_after_tap": true,
         "is_tapable": true,
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         }
     }')::jsonb
),
(
    '1316003df78d44168c61e80ce4c814bd',
    'Новая история',
    to_tsvector('Новая история'),
    'story',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    '2020-02-17T04:55:18+0000',
    'published',
    ARRAY['consumer2', 'my_consumer', 'consumer1']::TEXT[],
    ARRAY['restaurants','test']::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['main_screen']::TEXT[],
    42,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'my_exp',
    true,
    null,
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
                                "page": "2"
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
                "required": true,
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
    'deeplink_shortcut_id',
    'Диплинк-шорткат',
    to_tsvector('Диплинк-шорткат'),
    'deeplink_shortcut',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    '2020-02-17T04:55:18+0000',
    'published',
    ARRAY[]::TEXT[],
    ARRAY['restaurants','test']::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['main_screen']::TEXT[],
    42,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'my_exp_deeplinkshortcut',
    true,
    null,
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
                                "page": "2"
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
        "action": {
            "action_type": "deeplink",
            "content": "content"
        },
        "overlays": [{"text": "test_overlay_text"}],
        "meta_type": "deeplink_shortcut_meta_type",
        "is_attributed_text": true
    }')::jsonb
),
(
    '5831f5f73c784975976fb75328c85e35',
    'test fs background color',
    to_tsvector('test fs background color'),
    'fullscreen',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    null,
    'created',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['menu']::TEXT[],
    12,
    null,
    null,
    null,
    false,
    null,
    ('{
        "pages": [
            {
                "widgets": {
                    "close_button": {"color": "010102"},
                    "action_buttons": [
                        {"text": "Ясно", "color": "E7ECF2", "text_color": "21201f"}
                    ]
                },
                "backgrounds": [
                    {"type": "color", "content": "EA503F"},
                    "promotion_1c813a67-a4e7-45a3-968b-84b6cec554e9",
                    {
                        "widgets": {
                            "close_button": {"color": "010102"},
                            "action_buttons": [
                                {"text": "Понятно", "color": "E7ECF2", "text_color": "21201f"}
                            ]
                        },
                        "backgrounds": [
                            {"type": "color", "content": "3662B8"},
                            "promotion_5fac2e26-c168-47ad-a26a-88fa3deae82a"
                        ]
                    }
                ]
            }
        ]
    }')::jsonb,
    ('{}')::jsonb
),
(
    'id5',
    'test media_text in background',
    to_tsvector('test media_text in background'),
    'fullscreen',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    null,
    'published',
    null,
    ARRAY['tag3', 'tag4']::TEXT[],
    ARRAY['moscow', 'abakan']::TEXT[],
    ARRAY['main']::TEXT[],
    1,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'exp_fs',
    false,
    null,
    ('{
        "pages": [
            {
                "widgets": {
                    "close_button": {"color": "010102"},
                    "action_buttons": [
                        {"text": "Ясно", "color": "E7ECF2", "text_color": "21201f"}
                    ]
                },
                "backgrounds": [
                    {"type": "color", "content": "EA503F"},
                    "media_with_text_tag_id"
                ]
            }
        ]
    }')::jsonb,
    ('{}')::jsonb
),
(
    'id6',
    'fullscreen 6',
    to_tsvector('fullscreen 6'),
    'fullscreen',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    null,
    'published',
    null,
    ARRAY['tag3', 'tag4']::TEXT[],
    ARRAY['moscow', 'abakan']::TEXT[],
    ARRAY['main']::TEXT[],
    1,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    null,
    false,
    null,
    ('{
        "pages": [
            {
                "widgets": {
                    "close_button": {"color": "010102"},
                    "action_buttons": [
                        {"text": "Ясно", "color": "E7ECF2", "text_color": "21201f"}
                    ]
                },
                "backgrounds": [
                    {"type": "color", "content": "EA503F"},
                    "media_with_text_tag_id"
                ]
            }
        ]
    }')::jsonb,
    ('{ "campaign_labels": ["test_campaign_1", "test_campaign_2"]}')::jsonb
),
(
     'card_2',
     'banner card 2',
     to_tsvector('banner card 2'),
     'card',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['consumer1', 'consumer2']::TEXT[],
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
          "is_attributed_text": true,
          "campaign_labels": ["test_campaign_1", "test_campaign_2"]
       }'
     )::jsonb
),
(
     'notification_3',
     'banner notification 3',
     to_tsvector('banner notification 3'),
     'notification',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'archived',
     ARRAY['consumer1', 'my_consumer']::TEXT[],
     ARRAY['tag7', 'tag8']::TEXT[],
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
          "campaign_labels": ["test_campaign_1", "test_campaign_2"]
       }'
     )::jsonb
),
(
    '5e295aa23ebca0cf00e113eb',
    'legacy_story_5_stars_movies_2_ru',
    to_tsvector('legacy_story_5_stars_movies_2_ru'),
    'story',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    null,
    'published',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['NO_SCREEN']::TEXT[],
    1,
    '2020-10-02 15:04:08.751412',
    '2022-10-02 15:04:08.751412',
    'legacy_stories_fake_exp',
    false,
    null,
    ('{
        "pages": [
            {
                "widgets": {
                    "close_button": {"color": "21201F"},
                    "action_buttons": [
                        {
                            "text": "Купить билет",
                            "color": "FFDE40",
                            "action": {
                                "type": "web_view",
                                "payload": {
                                    "content": "https://widget.afisha.yandex.ru/w/venues/267"
                                }
                            },
                            "text_color": "0C1E40",
                            "is_tanker_key": false
                        }
                    ]
                },
                "autonext": true,
                "duration": 15,
                "backgrounds": [
                    {
                        "type": "image",
                        "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies/ru/3828fe88b582855934a8680f65c6a743c798e87d.jpeg"
                    }
                ]
            },
            {
                "widgets": {
                    "close_button": {"color": "21201F"},
                    "action_buttons": []
                },
                "autonext": true,
                "duration": 15,
                "backgrounds": [
                    {
                        "type": "image",
                        "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/005b27cbf2637cceb2c3dc8ac02581e5df84be24.jpg"
                    }
                ]
            },
            {
                "widgets": {
                    "close_button": {"color": "21201F"},
                    "action_buttons": []
                },
                "autonext": true,
                "duration": 15,
                "backgrounds": [
                    {
                        "type": "image",
                        "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/7c922d2d35f4bf25b483912fb43d932b3aae33ba.png"
                    }
                ]
            },
            {
                "widgets": {
                    "close_button": {"color": "21201F"},
                    "action_buttons": []
                },
                "autonext": true,
                "duration": 15,
                "backgrounds": [
                    {
                        "type": "image",
                        "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies_2/ru/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png"
                    }
                ]
            }
        ]
    }')::jsonb,
    ('{
        "active": true,
        "preview": {
            "text": {"color": "", "content": ""},
            "title": {"color": "", "content": ""},
            "backgrounds": [
                {
                    "type": "image",
                    "content": "https://promo-stories-testing.s3.mds.yandex.net/5_stars_movies/ru/3828fe88b582855934a8680f65c6a743c798e87d.jpeg"
                }
            ]
        },
        "meta_type": "old_story",
        "is_tapable": true,
        "story_context": "totw"
    }')::jsonb
),
(
    'promo_on_summary_id',
    'promo on summary',
    to_tsvector('promo on summary'),
    'promo_on_summary',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    '2020-02-17T04:55:18+0000',
    'published',
    ARRAY['cons1', 'cons2', 'my consumer']::TEXT[],
    ARRAY['restaurants','test']::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['main_screen']::TEXT[],
    42,
    '2019-05-22T16:51:09+0000',
    '2022-07-22T16:51:09+0000',
    'my_exp',
    false,
    null,
    ('{
        "pages": [{
            "title": {
                "items": [
                    {
                        "type": "image",
                        "image_tag": "ets_badge_icon",
                        "width": 15,
                        "vertical_alignment": "center",
                        "color": "000000"
                    },
                    {
                        "type": "text",
                        "text": "Eats: N minutes delivery",
                        "font_size": 14,
                        "font_weight": "bold",
                        "font_style": "italic",
                        "color": "000000"
                    }
                ]
            },
            "text": {
                "items": [
                    {
                        "type": "image",
                        "image_tag": "ets_badge_icon",
                        "width": 15,
                        "vertical_alignment": "center",
                        "color": "000000"
                    },
                    {
                        "type": "text",
                        "text": "Eats: N minutes delivery",
                        "font_size": 14,
                        "font_weight": "bold",
                        "font_style": "italic",
                        "color": "000000"
                    }
                ]
            },
            "icon": {
                "image_tag": "my_image_tag",
                "image_url": "http://here.is.url/with/path?and=query"
            },
            "widgets": {
                "deeplink_arrow_button": {
                    "deeplink": "https://plus.yandex.ru/card?utm_source=taxi&utm_medium=cpc&utm_campaign=fullscreen",
                    "color": "afafaf",
                    "items": [
                        {
                            "type": "image",
                            "image_tag": "ets_badge_icon",
                            "width": 15,
                            "vertical_alignment": "center",
                            "color": "000000"
                        },
                        {
                            "type": "text",
                            "text": "Eats: N minutes delivery",
                            "font_size": 14,
                            "font_weight": "bold",
                            "font_style": "italic",
                            "color": "000000"
                        }
                    ]
                },
                "actions_arrow_button": {
                    "actions": [
{
                  "alt_offer": {
                  "types": [
                    "combo_inner",
                    "combo_outer"
                  ]},
                  "type": "select_alt_offer"
                }
                    ],
                    "color": "afafaf",
                    "items": [
                        {
                            "type": "image",
                            "image_tag": "ets_badge_icon",
                            "width": 15,
                            "vertical_alignment": "center",
                            "color": "000000"
                        },
                        {
                            "type": "text",
                            "text": "go combo",
                            "font_size": 14,
                            "font_weight": "bold",
                            "font_style": "italic",
                            "color": "000000"
                        }
                    ]
                },
                "attributed_text": {
                    "items": [
                        {
                            "type": "image",
                            "image_tag": "ets_badge_icon",
                            "width": 15,
                            "vertical_alignment": "center",
                            "color": "000000"
                        },
                        {
                            "type": "text",
                            "text": "Eats: N minutes delivery",
                            "font_size": 14,
                            "font_weight": "bold",
                            "font_style": "italic",
                            "color": "000000"
                        }
                    ]
                },
                "drive_arrow_button": {
                    "color": "#afafaf",
                    "items": [
                        {
                            "type": "image",
                            "image_tag": "ets_badge_icon",
                            "width": 15,
                            "vertical_alignment": "center",
                            "color": "000000"
                        },
                        {
                            "type": "text",
                            "text": "Eats: N minutes delivery",
                            "font_size": 14,
                            "font_weight": "bold",
                            "font_style": "italic",
                            "color": "000000"
                        }
                    ]
                },
                "toggle": {
                    "is_selected": true,
                    "option_on": {
                        "text": {
                            "items": [
                                {
                                    "type": "image",
                                    "image_tag": "ets_badge_icon",
                                    "width": 15,
                                    "vertical_alignment": "center",
                                    "color": "000000"
                                }
                            ]
                        },
                        "title": {
                            "items": [
                                {
                                    "type": "image",
                                    "image_tag": "ets_badge_icon",
                                    "width": 15,
                                    "vertical_alignment": "center",
                                    "color": "000000"
                                }
                            ]
                        },
                        "actions": [
                            {
                                "type": "deeplink",
                                "extra": "extra_text"
                            }
                        ]
                    },
                    "option_off": {
                        "text": {
                            "items": [
                                {
                                    "type": "image",
                                    "image_tag": "ets_badge_icon",
                                    "width": 15,
                                    "vertical_alignment": "center",
                                    "color": "000000"
                                }
                            ]
                        },
                        "title": {
                            "items": [
                                {
                                    "type": "image",
                                    "image_tag": "ets_badge_icon",
                                    "width": 15,
                                    "vertical_alignment": "center",
                                    "color": "000000"
                                }
                            ]
                        },
                        "actions": [
                            {
                                "type": "deeplink",
                                "extra": "extra_text"
                            }
                        ]
                    }
                }
            }
        }]
    }')::jsonb,
    ('{
        "meta_type": "promo_block",
        "supported_classes": ["econom", "vip"],
        "show_policy": {
            "max_show_count": 3,
            "max_widget_usage_count": 1
        },
        "display_on": ["summary", "totw", "alt_offer"],
        "configuration": {
            "type": "list"
        },
        "feeds_admin_id": "11123"
    }')::jsonb
),
(
    '3ff01387-cc00-4928-bbd7-e3a80f06e774',
    'ultima promo',
    to_tsvector('ultima promo'),
    'promo_on_summary',
    '2020-09-21 11:50:05.648881',
    '2020-09-22 11:34:06.518764',
    '2020-09-21 11:50:05.648881',
    'published',
    NULL,
    ARRAY['ultima_vertical']::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['summary']::TEXT[],
    10,
    '2020-09-21 11:50:05.648881',
    '2022-07-22 16:51:09.000000',
    'promo_on_summary_ultima',
    false,
    NULL,
    ('{
        "pages": [
            {
                "text": {
                    "items": [
                        {
                            "text": "promo_on_summary.ultima.text",
                            "type": "text",
                            "color": "#AFAFAF",
                            "font_size": 14,
                            "is_tanker_key": true
                        }
                    ]
                },
                "title": {
                    "items": [
                        {
                            "text": "promo_on_summary.ultima.title",
                            "type": "text",
                            "is_tanker_key": true
                        }
                    ]
                },
                "widgets": {
                    "deeplink_arrow_button": {
                        "color": "#000000",
                        "items": [
                            {
                                "type": "image",
                                "width": 50,
                                "image_tag": "class_ultimate_icon_7"
                            }
                        ],
                        "deeplink": "yandextaxi://route?tariffClass=vip&vertical=ultima&expandingState=expanded"
                    }
                }
            }
        ]
    }')::jsonb,
    ('{
        "meta_type": "business_vip_promo_block",
        "show_policy": {
            "max_show_count": 1000,
            "max_widget_usage_count": 1000
        },
        "supported_classes": ["econom", "business", "comfortplus"]
    }')::jsonb
),
(
    'totw_banner_1', -- id
    'totw_banner_name', -- name
    to_tsvector('totw_banner_name'), -- name_tsv
    'totw_banner', -- promotion_type
    '2018-07-22T12:51:09.999999Z', -- created_at
    '2019-07-22T15:53:50.235707Z', -- updated_at
    '2020-09-17T16:53:50.235707Z', -- published_at
    'published', -- status
    NULL, -- consumers
    NULL, -- meta_tags
    ARRAY[]::TEXT[], -- zones
    ARRAY[]::TEXT[], -- screens
    5, -- priority
    '2020-09-17T16:53:50.235707Z', -- starts_at
    '2029-10-01T00:00:00.000000Z', -- ends_at
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
    'object_over_map_name', -- name
    to_tsvector('object_over_map_name'), -- name_tsv
    'object_over_map', -- promotion_type
    '2018-07-22T12:51:09.999999Z', -- created_at
    '2019-07-22T15:53:50.235707Z', -- updated_at
    '2020-09-17T16:53:50.235707Z', -- published_at
    'published', -- status
    NULL, -- consumers
    NULL, -- meta_tags
    ARRAY[]::TEXT[], -- zones
    ARRAY[]::TEXT[], -- screens
    5, -- priority
    '2020-09-07T16:53:50.235707Z', -- starts_at
    '2029-10-01T00:00:00.000000Z', -- ends_at
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
);
