INSERT INTO posm_templates (
    name,
    description,
    settings,
    visibility,
    created_at,
    updated_at,
    deleted_at
)
VALUES
(
    'template_1',
    'nice template',
    '{}',
    'global',
    NOW(),
    NOW(),
    NULL
),
(
    'awesome template',
    'another template',
    '{"qr": {"x": 50, "y": 50, "size": 40}, "text": {"x": 50, "y": 20, "color": "#FFFFFF"}}',
    'global',
    NOW(),
    NOW(),
    NULL
),
(
    'template_3',
    'deleted template',
    '{"qr": {"x": 50, "y": 50}, "text": {"x": 50, "y": 20}}',
    'global',
    NOW(),
    NOW(),
    NOW()
),
(
    'template_4',
    'restaurant template',
    '{"qr": {"x": 50, "y": 50, "size": 40}, "text": {"x": 50, "y": 20, "color": "#FFFFFF"}}',
    'restaurant',
    NOW(),
    NOW(),
    NULL
)
;
