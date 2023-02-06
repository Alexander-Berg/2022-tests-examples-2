insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_carousel',
    'Widget template 1',
    '{"carousel": "new"}'::jsonb,
    '{"title": "Бла бла бла"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 2',
    '{"place_filter_type": "open"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'banners',
    'Widget template 3',
    '{"format": "shortcut"}'::jsonb,
    '{"title": "Что-то еще"}'::jsonb,
    '{}'::jsonb
),
(
    'sorts',
    'Widget template 4',
    '{}'::jsonb,
    '{"title": ""}'::jsonb,
    '{}'::jsonb
),
(
    'filters',
    'Widget template 5',
    '{}'::jsonb,
    '{"title": ""}'::jsonb,
    '{}'::jsonb
),
(
    'timepickers',
    'Widget template 6',
    '{}'::jsonb,
    '{"title": ""}'::jsonb,
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
);

insert into constructor.layout_widgets (
    name,
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
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 2',
    2,
    1,
     '{"high": 3}'::jsonb,
     '{"title": "Три первых ресторана"}'::jsonb
),
(
    'Widget 3',
    3,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 4',
    1,
    1,
     '{"carousel": "promo"}'::jsonb,
     '{"title": "Акции и новинки"}'::jsonb
),
(
    'Widget 5',
    2,
    1,
     '{"low": 3}'::jsonb,
     '{"title": "Остальные места"}'::jsonb
),
(
    'Widget 6',
    2,
    1,
    '{"place_filter_type": "closed"}'::jsonb,
    '{"title": "Закрытые места"}'::jsonb
),
(
    'Widget 7',
    4,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 8',
    5,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 9',
    6,
    1,
     '{}'::jsonb,
     '{}'::jsonb
);
