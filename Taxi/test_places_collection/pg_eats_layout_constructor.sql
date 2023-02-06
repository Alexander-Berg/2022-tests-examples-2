insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_collection',
    'places_collection_list_template',
    '{"place_filter_type": "open", "output_type": "list"}'::jsonb,
    '{"title": "Рестораны"}'::jsonb,
    '{}'::jsonb
), 
(
    'places_collection',
    'places_collection_carousel_template',
    '{"place_filter_type": "open", "output_type": "carousel"}'::jsonb,
    '{"title": "Рестораны"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'deafult',
    'places_collection_layout',
    'egor-sorokin'
),
(

    'places_collection_slice',
    'places_collection_layout_2',
    'egor-sorokin'
),
(
    'places_collection_carousel',
    'places_collection_layout_3',
    'egor-sorokin'
),
(
    'places_collection_exclude_brands',
    'places_collection_layout_4',
    'egor-sorokin'
),
(
    'places_collection_min_count',
    'places_collection_layout_5',
    'egor-sorokin'
),
(
    'places_collection_promo',
    'places_collection_layout_6',
    'egor-sorokin'
),
(
    'places_collection_exclude_businesses',
    'places_collection_layout_7',
    'egor-sorokin'
),
(
    'places_collection_disable_filters',
    'places_collection_layout_8',
    'egor-sorokin'
),
(
    'places_collection_history_order',
    'places_collection_layout_9',
    'egor-sorokin'
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
    'open_places',
    1,
    1,
    1,
    '{}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'slice_open_places',
    2,
    1,
    2,
    '{"low": 2, "limit": 2}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'carousel_open_places',
    3,
    2,
    3,
    '{}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'exclude_brands',
    4,
    1,
    4,
    '{"exclude_brands": [3, 4]}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'min_count',
    5,
    1,
    5,
    '{"min_count": 4}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'promo',
    6,
    1,
    6,
    '{"place_filter_type": "promo"}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'exclude_businesses',
    7,
    1,
    7,
    '{"exclude_businesses": ["shop", "store"]}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'disable_filters',
    8,
    1,
    8,
    '{"disable_filters": true}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
),
(
    'history_order',
    9,
    1,
    9,
    '{"place_filter_type": "open", "selection": "history_order"}'::jsonb,
    '{"title": "Рестораны"}'::jsonb
);
