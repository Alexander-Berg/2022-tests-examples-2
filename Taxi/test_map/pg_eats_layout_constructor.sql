insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
    'pickup_places_list',
    'Pickup Places List Template',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),(
    'filters',
    'FILTERS_TEMPLATE',
    '{"mode":"map"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),(
    'timepickers',
    'timepickers_template',
    '{"mode":"map"}'::jsonb,
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
    'Simple layout',
    'map_pickup',
    's-grechkin'
);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
    'place_layout',
    'order_existing',
    'Order Actions and Meta',
    '{
        "order":["actions", "meta"],
        "action_extenders":["actions_info", "actions_promo", "actions_review"],
        "meta_extenders":["meta_yandex_plus", "meta_rating", "meta_price_category", "meta_info"]
    }'::jsonb
),(
    'filters_layout',
    'filters_v1',
    'Filters v1 Meta Widget',
    '{}'::jsonb
),
(
    'filters_layout',
    'filters_v2',
    'Filters v2 Meta Widget',
    '{
        "filters_v2": true,
        "list": {
            "end_icon_treshold": 1,
            "filters_groups": [
                {
                    "include_slugs": [
                    "sushi",
                    "burgers",
                    "pizza"
                    ]
                }
            ],
            "limit": 2
        }
     }'::jsonb
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
)
values
(
    'Filters',
    2,
    2,
    1,
    '{}'::jsonb,
    '{}'::jsonb,
    NULL,
    'meta_widget_experiment'
),(
    'Places List 1',
    1,
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb,
    1,
    NULL
),(
    'TimePickers',
    3,
    3,
    1,
     '{}'::jsonb,
     '{}'::jsonb,
     NULL,
     NULL
);
