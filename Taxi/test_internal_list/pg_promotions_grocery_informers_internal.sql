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
     'grocery_informer1',
     'published_ok',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "published_ok"
             }
         ]
     }')::jsonb,
     'Grocery Informer',
     to_tsvector('Grocery Informer'),
     'grocery_informer',
     '2019-07-22T16:51:09+0000',
     '2019-07-23T16:51:09+0000',
     '2019-07-24T16:51:09+0000',
     'published',
     NULL,
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     NULL,
     false,
     NULL,
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
     'grocery_informer2',
     'published_ok',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "published_ok"
             }
         ]
     }')::jsonb,
     'Grocery Informer 2',
     to_tsvector('Grocery Informer 2'),
     'grocery_informer',
     '2019-07-22T16:51:09+0000',
     '2019-07-23T16:51:09+0000',
     '2019-07-24T16:51:09+0000',
     'published',
     NULL,
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'grocery_experiment',
     false,
     NULL,
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
             "additional_text": "More text",
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
