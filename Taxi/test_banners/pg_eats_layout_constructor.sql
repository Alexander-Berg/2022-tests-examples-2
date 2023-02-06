insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
    'banners',
    'Widget template 1',
    '{"format":"classic"}'::jsonb,
    '{"title": "Баннеры"}'::jsonb,
    '{}'::jsonb
),
(
    'banners',
    'shortcuts',
    '{"format":"shortcut"}'::jsonb,
    '{"title": "шорткаты"}'::jsonb,
    '{}'::jsonb
),
(
    'banners',
    'wide_banner',
    '{"format":"wide_and_short"}'::jsonb,
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
    'nevladov'
),
(
    'Layout 2',
    'layout_2',
    'nevladov'
),
(
    'Layout 3',
    'layout_3',
    'nevladov'
),
(
    'Layout 4',
    'layout_4',
    'nevladov'
),
(
    'Layout 5',
    'layout_5',
    'nevladov'
),
(
    'Layout 6',
    'layout_6',
    'nevladov'
),
(
    'Banners required',
    'source_required',
    'mazgutov'
),
(
    'Banners not required',
    'source_not_required',
    'mazgutov'
),
(
    'shortcut and wide banners',
    'shortcut_wide',
    'udalovmax'
),
(
    'all banners',
    'all_banners',
    'udalovmax'
),
(
    'random banners',
    'random_banners',
    'udalovmax'
),
(
    'conditional_banners',
    'conditional_banners',
    'nk2ge5k'
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
    'Widget 1',
    1,
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 2',
    2,
    1,
    2,
     '{"banner_types": ["info", "collection"]}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 3',
    3,
    1,
    3,
     '{"banners_id": [2, 3], "format": "shortcut"}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 4',
    4,
    1,
    4,
     '{"exclude": [1]}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 5',
    5,
    1,
    5,
     '{"format": "classic"}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 6',
    6,
    1,
    6,
     '{"format": "shortcut"}'::jsonb,
     '{"title": "Баннеры shortcut"}'::jsonb
),
(
    'Widget 7',
    7,
    1,
    6,
     '{"banners_id": [1, 4, 5], "min_count": 2}'::jsonb,
     '{"title": "Баннеры не попадут в layout из-за min_count"}'::jsonb
),
(
    'Widget 8',
    8,
    1,
    6,
     '{"limit": 1}'::jsonb,
     '{"title": "Попадет только первый баннер из-за limit"}'::jsonb
),
(
    'required',
    9,
    1,
    7,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'not_required',
    10,
    1,
    8,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'shortcut',
    11,
    2,
    9,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'wide',
    12,
    3,
    9,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Classic banners',
    13,
    1,
    10,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Shortcut banners',
    14,
    2,
    10,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Wide banners',
    15,
    3,
    10,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Random banners',
    16,
    1,
    11,
    '{"randomize":true}'::jsonb,
    '{}'::jsonb
),
(
    'conditional_banners',
    17,
    1,
    12,
    '{
        "surge_condition": {
            "min_surge_places_count": 1,
            "exclude_businesses": ["shop"],
            "limit": 10
        }
    }'::jsonb,
    '{}'::jsonb
);
