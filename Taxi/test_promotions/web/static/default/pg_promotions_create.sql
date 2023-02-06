-- media_tags we should return in view handle
INSERT INTO promotions.media_tags (
    id,
    type,
    resize_mode,
    sizes
) VALUES (
    'promotion_1c813a67-a4e7-45a3-968b-84b6cec554e9',
    'image',
    'original_only',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        }
    ]}')::jsonb
), (
    'promotion_5fac2e26-c168-47ad-a26a-88fa3deae82a',
    'image',
    'original_only',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        }
    ]}')::jsonb
);
