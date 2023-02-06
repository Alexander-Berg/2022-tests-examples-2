insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_list',
    'Open places',
    '{"place_filter_type": "open"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Basic header widget',
    '{"text": "rest.1", "note": {"type": "eats_free_delivery"}}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Header widget with button and styles',
    '{
        "text": "rest.2",
        "styles_json": "{\"bold\": true}",
        "button_json": "{\"text\": \"all\", \"deeplink\": \"eda.yandex://collections/places\"}"
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Header widget depends on one',
    '{
        "text": "rest.3",
        "depends_on_any": [
            "6_places_list"
        ]
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Header widget depends on two',
    '{
        "text": "rest.4",
        "depends_on_any": [
            "999_places_list",
            "8_places_list"
        ]
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Header widget depends on unknown',
    '{
        "text": "rest.5",
        "depends_on_any": [
            "999_unkwnown"
        ]
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'header',
    'Header widget depends on empty string',
    '{
        "text": "rest.5",
        "depends_on_any": [
            ""
        ]
    }'::jsonb,
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
    'Basic header',
    'basic_header_1',
    'superpaintman'
),
(
    'Header with button and styles',
    'header_with_button_and_styles_1',
    'superpaintman'
),
(
    'Header depends on one',
    'header_depends_on_one_1',
    'superpaintman'
),
(
    'Header depends on two',
    'header_depends_on_two_1',
    'superpaintman'
),
(
    'Header depends on unknown',
    'header_depends_on_unknown_1',
    'superpaintman'
),
(
    'Header depends on empty string',
    'header_depends_on_empty_string_1',
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
-- Basic header
(
    'Header',
    1,
    2,
    1,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    2,
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb
),

-- Header with button and styles
(
    'Header',
    3,
    3,
    2,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    4,
    1,
    2,
    '{}'::jsonb,
    '{}'::jsonb
),

-- Header depends on one
(
    'Header',
    5,
    4,
    3,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    6,
    1,
    3,
    '{}'::jsonb,
    '{}'::jsonb
),

-- Header depends on two
(
    'Header',
    7,
    5,
    4,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    8,
    1,
    4,
    '{}'::jsonb,
    '{}'::jsonb
),

-- Header depends on unknown
(
    'Header',
    9,
    6,
    5,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    10,
    1,
    5,
    '{}'::jsonb,
    '{}'::jsonb
),

-- Header depends on empty string
(
    'Header',
    11,
    7,
    6,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Place list',
    12,
    1,
    6,
    '{}'::jsonb,
    '{}'::jsonb
);
