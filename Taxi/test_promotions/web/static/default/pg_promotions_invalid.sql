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
    'totw_banner_invalid_1', -- id
    'totw_banner_invalid_name', -- name
    to_tsvector('totw_banner_invalid_name'), -- name_tsv
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
    '2022-10-01T00:00:00.000000Z', -- ends_at
    'totw_banner_exp', -- experiment
    false, -- has_yql_data
    NULL, -- yql_data
    ('
        {
            "pages": [
                {
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
);
