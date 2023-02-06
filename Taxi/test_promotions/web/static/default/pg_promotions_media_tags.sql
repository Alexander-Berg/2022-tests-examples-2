INSERT INTO promotions.media_tags (
    id,
    type,
    resize_mode,
    sizes
) VALUES (
    'f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag1',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        },
        {
            "field": "screen_height",
            "value": 480,
            "mds_id": "height_480_mds_id",
            "url": "http://mds.net/height_480_mds_id"
        },
        {
            "field": "screen_height",
            "value": 1334,
            "mds_id": "height_1334_mds_id",
            "url": "http://mds.net/height_1334_mds_id"
        },
        {
            "field": "screen_height",
            "value": 1920,
            "mds_id": "height_1920_mds_id",
            "url": "http://mds.net/height_1920_mds_id"
        }
    ]}')::jsonb
), (
    'f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag2',
    'image',
    'width_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        },
        {
            "field": "screen_width",
            "value": 320,
            "mds_id": "width_320_mds_id",
            "url": "http://mds.net/width_320_mds_id"
        },
        {
            "field": "screen_width",
            "value": 750,
            "mds_id": "width_750_mds_id",
            "url": "http://mds.net/width_750_mds_id"
        },
        {
            "field": "screen_width",
            "value": 1080,
            "mds_id": "width_1080_mds_id",
            "url": "http://mds.net/width_1080_mds_id"
        }
    ]}')::jsonb
), (
    'f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag3',
    'image',
    'scale_factor',
    ('{"sizes":[
        {
            "field": "scale",
            "value": 1,
            "mds_id": "scale_1_mds_id",
            "url": "http://mds.net/scale_1_mds_id"
        },
        {
            "field": "scale",
            "value": 1.5,
            "mds_id": "scale_1_mds_id",
            "url": "http://mds.net/scale_1.5_mds_id"
        },
        {
            "field": "scale",
            "value": 3,
            "mds_id": "scale_3_mds_id",
            "url": "http://mds.net/scale_3_mds_id"
        }
    ]}')::jsonb
), (
    'media_tag_id1',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        },
        {
            "field": "screen_height",
            "value": 480,
            "mds_id": "height_480_mds_id",
            "url": "http://mds.net/height_480_mds_id"
        },
        {
            "field": "screen_height",
            "value": 1334,
            "mds_id": "height_1334_mds_id",
            "url": "http://mds.net/height_1334_mds_id"
        },
        {
            "field": "screen_height",
            "value": 1920,
            "mds_id": "height_1920_mds_id",
            "url": "http://mds.net/height_1920_mds_id"
        }
    ]}')::jsonb
), (
    'media_tag_id2',
    'image',
    'width_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id"
        },
        {
            "field": "screen_width",
            "value": 320,
            "mds_id": "width_320_mds_id",
            "url": "http://mds.net/width_320_mds_id"
        },
        {
            "field": "screen_width",
            "value": 750,
            "mds_id": "width_750_mds_id",
            "url": "http://mds.net/width_750_mds_id"
        },
        {
            "field": "screen_width",
            "value": 1080,
            "mds_id": "width_1080_mds_id",
            "url": "http://mds.net/width_1080_mds_id"
        }
    ]}')::jsonb
), (
    'media_tag_id3',
    'image',
    'scale_factor',
    ('{"sizes":[
        {
            "field": "scale",
            "value": 1,
            "mds_id": "scale_1_mds_id",
            "url": "http://mds.net/scale_1_mds_id"
        },
        {
            "field": "scale",
            "value": 1.5,
            "mds_id": "scale_1_mds_id",
            "url": "http://mds.net/scale_1.5_mds_id"
        },
        {
            "field": "scale",
            "value": 3,
            "mds_id": "scale_3_mds_id",
            "url": "http://mds.net/scale_3_mds_id"
        }
    ]}')::jsonb
),
(
    'media_with_text_tag_id',
    'image',
    'height_fit',
    ('{"sizes":[
        {
            "field": "original",
            "value": 0,
            "mds_id": "original_mds_id",
            "url": "http://mds.net/original_mds_id",
            "media_text": "picture_text"
        }    
    ]}')::jsonb
);
