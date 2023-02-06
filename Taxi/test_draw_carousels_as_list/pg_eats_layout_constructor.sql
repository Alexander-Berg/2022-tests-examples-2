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
    '{"carousel": "new", "min_count": 10}'::jsonb,
    '{"title": "Бла бла бла"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 2',
    '{"low": 2, "place_filter_type": "open"}'::jsonb,
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
    'Catalog required',
    'source_required',
    'mazgutov'
),
(
    'Catalog not required',
    'source_not_required',
    'mazgutov'
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
     '{"carousel": "promo", "min_count": 1}'::jsonb,
     '{"title": "Акции и новинки"}'::jsonb
),
(
    'Widget 2',
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 3',
    1,
    2,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 4',
    1,
    2,
     '{"carousel": "taxi-delivery", "min_count": 5}'::jsonb,
     '{"title": "Теперь доедет"}'::jsonb
),
(
    'Widget 5',
    2,
    4,
     '{"high": 2, "low": 0}'::jsonb,
     '{"title": "Два первых ресторана"}'::jsonb
),
(
    'Widget 6',
    2,
    4,
     '{"high": 4}'::jsonb,
     '{"title": "Два следующих ресторана"}'::jsonb
),
(
    'Widget 7',
    2,
    4,
     '{"low": 4}'::jsonb,
     '{"title": "Все оставшиеся рестораны"}'::jsonb
),
(
    'required',
    2,
    5,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'not_required',
    2,
    6,
    '{}'::jsonb,
    '{}'::jsonb
);
