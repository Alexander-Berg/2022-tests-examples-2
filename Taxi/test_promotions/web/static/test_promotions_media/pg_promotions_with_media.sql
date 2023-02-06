INSERT INTO promotions.promotions (
    id,
    name,
    revision_history,
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
    extra_fields
) VALUES
(
    'story_view_id',
    'banner 1',
    null,
    to_tsvector('banner 1'),
    'story',
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
    null,
    false,
    null,
    ('{"pages": [
        {
            "image": "media_tag_id1",
            "icon": "media_tag_id1",
            "backgrounds": [
                "media_tag_id1",
                {"type": "color", "content": "aeaeae"}
            ],
            "widgets": {
                "action_buttons": []
            }
        }
    ]}')::jsonb,
    ('{
        "preview": {
            "main_view": {
                "type": "image",
                "content": "url"
            },
            "backgrounds": [
                {
                    "type": "color",
                    "content": "AEAEAE"
                },
                {
                    "type": "image",
                    "content": "url"
                }
            ]
        }
    }')::jsonb
),
(
    'story_for_edit',
    'banner for edit',
    null,
    to_tsvector('banner for edit'),
    'fullscreen',
    '2019-10-04 07:39:09.140720 +00:00',
    '2019-10-04 07:39:09.140720 +00:00',
    null,
    'created',
    ARRAY[]::TEXT[],
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
            "image": "media_tag_id2",
            "icon": "media_tag_id2",
            "backgrounds": [
                "media_tag_id2",
                {"type": "color", "content": "aeaeae2"}
            ],
            "widgets": {
                "action_buttons": []
            }
        }
    ]}')::jsonb,
    ('{
        "preview": {
            "main_view": {
                "type": "image",
                "content": "url2"
            },
            "backgrounds": [
                {
                    "type": "color",
                    "content": "AEAEAE2"
                },
                {
                    "type": "image",
                    "content": "url2"
                }
            ]
        }
    }')::jsonb
),
(
    'card_id',
    'banner 4',
    null,
    to_tsvector('banner 4'),
    'card',
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
    null,
    false,
    null,
    ('{"pages": [
        {
            "image": "media_tag_id1",
            "icon": "media_tag_id1",
            "backgrounds": [
                "media_tag_id1",
                {"type": "color", "content": "aeaeae"}
            ],
            "widgets": {
                "action_buttons": []
            }
        }
    ]}')::jsonb,
    null
),
(
    'fullscreen_id',
    'banner 3',
    null,
    to_tsvector('banner 3'),
    'fullscreen',
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
    null,
    false,
    null,
    ('{"pages": [
        {
            "image": "media_tag_id1",
            "icon": "media_tag_id1",
            "backgrounds": [
                "media_tag_id1",
                {"type": "color", "content": "aeaeae"}
            ],
            "widgets": {
                "action_buttons": []
            }
        }
    ]}')::jsonb,
    null
);
