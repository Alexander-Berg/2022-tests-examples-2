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
    'banners',
    'shortcuts',
    '{"format":"shortcut"}'::jsonb,
    '{"title": "шорткаты"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Something went wrong',
    'fallback_layout',
    'mazgutov'
),
(
    'Integer overflow',
    'integer_overflow',
    'nk2ge5k'
),
(
    'Integer overflow and carousel',
    'integer_overflow_and_carousel',
    'nk2ge5k'
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
     '{"title": "Carousel for errors"}'::jsonb
),
(
    'Banners with integer overflow',
    2,
    2,
     '{"exclude": [2667931318795052500]}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 1',
    1,
    3,
     '{}'::jsonb,
     '{"title": "Carousel for errors"}'::jsonb
),
(
    'Banners with integer overflow',
    2,
    3,
     '{"exclude": [2667931318795052500]}'::jsonb,
     '{}'::jsonb
);
