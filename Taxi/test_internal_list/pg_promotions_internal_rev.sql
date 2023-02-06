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
     'story_id111',
     'published_ok',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "published_ok"
             }
         ]
     }')::jsonb,
     'story 2',
     to_tsvector('story 2'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     'published',
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
                "backgrounds": [{"type": "color", "content": "aeaeae"}],
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
     'id2',
     'republished',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T15:51:09+0000",
                 "revision": "published_ok"
             },
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "republished"
             }
         ]
     }')::jsonb,
     'banner 12',
     to_tsvector('banner 12'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
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
    ('{"pages": [{"text": {"color": "E7ECF2", "content": "First slide lorem ipsum"}, "title": {"color": "002864", "content": "first.slide.key", "is_tanker_key": true}, "widgets": {"link": {"text": "First slide link text", "action": {"type": "move", "payload": {"page": 2}}, "text_color": "00691F"}, "pager": {"color_on": "3662B8", "color_off": "237DC6"}, "menu_button": {"color": "E14138"}, "action_buttons": [{"text": "Action button text", "color": "143264", "action": {"type": "deeplink", "payload": {"content": "protocol://deeplink", "need_authorization": true}}, "text_color": "ECE2C9"}]}, "autonext": true, "duration": 11, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/48555801fd6047f2a9ac5fdb2f0c9330.jpg"}, "backgrounds": [{"type": "color", "content": "FFDE40"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/04ed6f74739842a7ad06d3cfa178c4e1.jpg"}]}, {"text": {"color": "8590A2", "content": "Text and title. Background only with image"}, "title": {"color": "D68F37", "content": "Second slide normal title", "is_tanker_key": false}, "widgets": {"link": {"text": "link.key", "text_color": "820000", "is_tanker_key": true}, "action_buttons": [{"text": "action.button.key", "color": "820000", "text_color": "998E76", "is_tanker_key": true}]}, "duration": 33, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/96619b0d67e04b1c923acfc598d8999d.jpg"}, "backgrounds": [{"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/4ef4e8987ed54847857c943c426268f2.jpg"}]}]}')::jsonb,
    ('{"preview": {"text": {"color": "B1AEEB", "content": "Lorem ipsum dolor sit amet"}, "title": {"color": "FFDE40", "content": "preview.title.key", "is_tanker_key": true}, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/b99a7261daf447d3b85c413e91d6a8a3.jpg"}, "backgrounds": [{"type": "color", "content": "EA503F"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/c7d1c7f3f07b48d5ae6e059c15045788.jpg"}]}, "is_tapable": true, "mark_read_after_tap": false}')::jsonb
),
(
     'id4',
     'republished_twice_archived',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T14:51:09+0000",
                 "revision": "published_ok1"
             },
             {
                 "created_at": "2019-07-22T15:51:09+0000",
                 "revision": "published_ok2"
             },
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "republished_twice_archived"
             }
         ]
     }')::jsonb,
     'banner 4',
     to_tsvector('banner 4'),
     'story',
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
    ('{"pages": [{"text": {"color": "E7ECF2", "content": "First slide lorem ipsum"}, "title": {"color": "002864", "content": "first.slide.key", "is_tanker_key": true}, "widgets": {"link": {"text": "First slide link text", "action": {"type": "move", "payload": {"page": "2"}}, "text_color": "00691F"}, "pager": {"color_on": "3662B8", "color_off": "237DC6"}, "menu_button": {"color": "E14138"}, "action_buttons": [{"text": "Action button text", "color": "143264", "action": {"type": "deeplink", "payload": {"content": "protocol://deeplink", "need_authorization": true}}, "text_color": "ECE2C9"}]}, "autonext": true, "duration": 11, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/48555801fd6047f2a9ac5fdb2f0c9330.jpg"}, "backgrounds": [{"type": "color", "content": "FFDE40"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/04ed6f74739842a7ad06d3cfa178c4e1.jpg"}]}, {"text": {"color": "8590A2", "content": "Text and title. Background only with image"}, "title": {"color": "D68F37", "content": "Second slide normal title", "is_tanker_key": false}, "widgets": {"link": {"text": "link.key", "text_color": "820000", "is_tanker_key": true}, "action_buttons": [{"text": "action.button.key", "color": "820000", "text_color": "998E76", "is_tanker_key": true}]}, "duration": 33, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/96619b0d67e04b1c923acfc598d8999d.jpg"}, "backgrounds": [{"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/4ef4e8987ed54847857c943c426268f2.jpg"}]}]}')::jsonb,
    ('{"preview": {"text": {"color": "B1AEEB", "content": "Lorem ipsum dolor sit amet"}, "title": {"color": "FFDE40", "content": "preview.title.key", "is_tanker_key": true}, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/b99a7261daf447d3b85c413e91d6a8a3.jpg"}, "backgrounds": [{"type": "color", "content": "EA503F"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/c7d1c7f3f07b48d5ae6e059c15045788.jpg"}]}, "is_tapable": true, "mark_read_after_tap": false}')::jsonb
),
(
     'id4444',
     'republished_twice_published',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T14:51:09+0000",
                 "revision": "published_ok1"
             },
             {
                 "created_at": "2019-07-22T15:51:09+0000",
                 "revision": "published_ok2"
             },
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "republished_twice_published"
             }
         ]
     }')::jsonb,
     'banner 4444',
     to_tsvector('banner 4444'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag7', 'tag8']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
    ('{"pages": [{"text": {"color": "E7ECF2", "content": "First slide lorem ipsum"}, "title": {"color": "002864", "content": "first.slide.key", "is_tanker_key": true}, "widgets": {"link": {"text": "First slide link text", "action": {"type": "move", "payload": {"page": "2"}}, "text_color": "00691F"}, "pager": {"color_on": "3662B8", "color_off": "237DC6"}, "menu_button": {"color": "E14138"}, "action_buttons": [{"text": "Action button text", "color": "143264", "action": {"type": "deeplink", "payload": {"content": "protocol://deeplink", "need_authorization": true}}, "text_color": "ECE2C9"}]}, "autonext": true, "duration": 11, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/48555801fd6047f2a9ac5fdb2f0c9330.jpg"}, "backgrounds": [{"type": "color", "content": "FFDE40"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/04ed6f74739842a7ad06d3cfa178c4e1.jpg"}]}, {"text": {"color": "8590A2", "content": "Text and title. Background only with image"}, "title": {"color": "D68F37", "content": "Second slide normal title", "is_tanker_key": false}, "widgets": {"link": {"text": "link.key", "text_color": "820000", "is_tanker_key": true}, "action_buttons": [{"text": "action.button.key", "color": "820000", "text_color": "998E76", "is_tanker_key": true}]}, "duration": 33, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/96619b0d67e04b1c923acfc598d8999d.jpg"}, "backgrounds": [{"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/4ef4e8987ed54847857c943c426268f2.jpg"}]}]}')::jsonb,
    ('{"preview": {"text": {"color": "B1AEEB", "content": "Lorem ipsum dolor sit amet"}, "title": {"color": "FFDE40", "content": "preview.title.key", "is_tanker_key": true}, "main_view": {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/b99a7261daf447d3b85c413e91d6a8a3.jpg"}, "backgrounds": [{"type": "color", "content": "EA503F"}, {"type": "image", "content": "https://taxi-promotions-testing.s3.mdst.yandex.net/c7d1c7f3f07b48d5ae6e059c15045788.jpg"}]}, "is_tapable": true, "mark_read_after_tap": false}')::jsonb
),
(
     'story_id1',
     'archived',
     ('{
         "data": [
             {
                 "created_at": "2019-07-20T16:51:09+0000",
                 "revision": "archived"
             }
         ]
     }')::jsonb,
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
                "backgrounds": [{"type": "color", "content": "aeaeae"}],
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
     'deeplink_shortcut_id1',
     'archived',
     ('{
         "data": [
             {
                 "created_at": "2019-07-20T16:51:09+0000",
                 "revision": "archived"
             }
         ]
     }')::jsonb,
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
                "backgrounds": [{"type": "color", "content": "aeaeae"}],
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
        "meta_type": "deeplink_shortcut_meta_type"
    }')::jsonb
),
(
    '5831f5f73c784975976fb75328c85e35',
    'revision',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "revision"
             }
         ]
     }')::jsonb,
    'test fs background color',
    to_tsvector('test fs background color'),
    'fullscreen',
    '2019-07-22T16:51:09+0000',
    '2019-07-22T16:51:09+0000',
    null,
    'created',
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
);
