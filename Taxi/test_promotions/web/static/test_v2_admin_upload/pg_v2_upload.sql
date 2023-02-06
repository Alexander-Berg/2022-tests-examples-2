
INSERT INTO promotions.media_tags (
    id,
    type,
    resize_mode,
    sizes
) VALUES (
    'f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag1',
    'image',
    'original_only',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id",
            "url": "http://ttt.ru/858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id"
        }
    ]}')::jsonb
), (
    'f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag2',
    'image',
    'original_only',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id",
            "url": "http://ttt.ru/858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id"
        }
    ]}')::jsonb
), (
    '1234-5678_media_tag_id',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id",
            "url": "http://ttt.ru/858a1a15-159d-4d06-9b3c-abd4d92f7039_mds_id"
        }
    ]}')::jsonb
);

