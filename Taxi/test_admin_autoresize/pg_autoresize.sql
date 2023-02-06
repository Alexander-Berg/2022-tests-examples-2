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
    'banner_with_media_tag_ok_image_height_fit',
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
            "backgrounds": ["media_tag_ok_image_height_fit"],
            "widgets": {"action_buttons": []}
        }
    ]}')::jsonb,
    null
),
(
    'banner_with_media_tag_ok_image_width_fit',
    'banner 2',
    to_tsvector('banner 2'),
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
            "backgrounds": ["media_tag_ok_image_width_fit"],
            "widgets": {"action_buttons": []}
        }
    ]}')::jsonb,
    null
),
(
    'banner_with_media_tag_ok_image_scale_factor',
    'banner 3',
    to_tsvector('banner 3'),
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
            "backgrounds": ["media_tag_ok_image_scale_factor"],
            "widgets": {"action_buttons": []}
        }
    ]}')::jsonb,
    null
);

INSERT INTO promotions.media_tags (
    id,
    type,
    resize_mode,
    sizes
) VALUES
(
    'media_tag_ok_image_height_fit',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "original_url"
        }
    ]}')::jsonb
),
(
    'media_tag_ok_image_width_fit',
    'image',
    'width_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "original_url"
        }
    ]}')::jsonb
),
(
    'media_tag_ok_image_scale_factor',
    'image',
    'scale_factor',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "original_url"
        }
    ]}')::jsonb
),
(
    'media_tag_without_original',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field":"screen_height",
            "value":720,
            "mds_id": "mds_id",
            "url": "some_url"
        }
    ]}')::jsonb
),
(
    'media_tag_wrong_type',
    'wrong_type',
    'height_fit',
    ('{"sizes":[]}')::jsonb
);
