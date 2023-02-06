insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'filters',
    'FILTERS_TEMPLATE',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
), (
    'places_list',
    'LIST_TEMPLATE',
    '{"place_filter_type": "open"}'::jsonb,
    '{}'::jsonb,
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
    'filters_v2_layout',
    'user'
);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'filters_layout',
     'default',
     'Default',
     '{}'::jsonb
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload,
    meta_widget,
    meta_widget_experiment_name
) values (
    'Filters',
    1,
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb,
    NULL,
    'meta_widget_experiment'
),
(
    'Places',
    2,
    2,
    1,
    '{"carousel": "promo", "min_count": 5}'::jsonb,
    '{"title": "Акции и новинки"}'::jsonb,
    NULL,
    NULL
),
(
    'Places',
    3,
    2,
    2,
    '{"carousel": "promo", "min_count": 5}'::jsonb,
    '{"title": "Плейсы после применения фильтров 2.0"}'::jsonb,
    NULL,
    NULL
);
