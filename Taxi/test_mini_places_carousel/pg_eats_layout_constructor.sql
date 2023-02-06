insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'mini_places_carousel',
    'Mini shops carouseel',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Layout 1',
    'layout_1',
    'superpaintman'
),
(
    'Layout 2',
    'layout_2',
    'superpaintman'
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload
)
values
(
    'Mini shops carouseel',
    1,
    1,
    1,
    '{"brands_order": [30, 20, 10], "image_source": "logo"}'::jsonb,
    '{}'::jsonb
),
(
    'Mini shops carouseel with default place_filter_type',
    2,
    1,
    2,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Mini shops carouseel with open place_filter_type',
    3,
    1,
    2,
    '{"place_filter_type":"open"}'::jsonb,
    '{}'::jsonb
),
(
    'Mini shops carouseel with any place_filter_type',
    4,
    1,
    2,
    '{"place_filter_type":"any"}'::jsonb,
    '{}'::jsonb
),
(
    'Mini shops carouseel with shop or store',
    5,
    1,
    2,
    '{"place_filter_type":"any", "include_businesses": ["shop", "store"]}'::jsonb,
    '{}'::jsonb
);
