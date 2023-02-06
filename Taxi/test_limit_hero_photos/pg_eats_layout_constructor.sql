insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
) values (
    'places_carousel',
    'Widget template 1',
    '{}'::jsonb,
    '{"title": "Карусель"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 2',
    '{}'::jsonb,
    '{"title": "Список"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
) values (
    'Layout 1',
    'layout_1',
    'user'
), (
    'Layout 2',
    'layout_2',
    'user'

);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'place_layout',
     'two_photos',
     'photo limit 2',
     '{
        "order":[],
        "action_extenders":[],
        "meta_extenders":[],
        "hero_photo": {"limit": 2}
     }'::jsonb
),
(
     'place_layout',
     'default_limit',
     'photo limit default',
     '{
       "order":[],
       "action_extenders":[],
       "meta_extenders":[]
     }'::jsonb
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload,
    meta_widget
) values (
    'Layout 1 Widget 1',
    1,
    1,
    1,
     '{"carousel": "new", "min_count": 1}'::jsonb,
     '{}'::jsonb,
    1
),
(
    'Layout 1 Widget 2',
    2,
    2,
    1,
     '{"low": 0, "place_filter_type": "open"}'::jsonb,
     '{}'::jsonb,
    1
), (
    'Layout 2 Widget 1',
    3,
    1,
    2,
     '{"carousel": "new", "min_count": 1}'::jsonb,
     '{}'::jsonb,
    2
),
(
    'Layout 2 Widget 2',
    4,
    2,
    2,
     '{"low": 0, "place_filter_type": "open"}'::jsonb,
     '{}'::jsonb,
    2
);
