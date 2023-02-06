insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_collection',
    'Selection',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'place_layout',
     'first',
     'First meta widget',
     '{
       "order":["meta"],
       "action_extenders": [],
       "meta_extenders":["meta_price_category"]
     }'::jsonb
),
(
     'place_layout',
     'second',
     'Second meta widget',
     '{
       "order":["meta", "actions"],
       "meta_extenders":["meta_price_category", "meta_rating"],
       "action_extenders": ["actions_promo"]
     }'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Layout 1',
    'places_selection',
    'nk2ge5k'
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload,
    meta_widget
)
values
(
    'Selection open list',
    1,
    1,
    1,
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "selection": "history_order"
    }'::jsonb,
    '{}'::jsonb,
    1
),
(
    'Selection any carousel',
    2,
    1,
    1,
    '{
        "place_filter_type": "any",
        "output_type": "carousel",
        "selection": "history_order"
    }'::jsonb,
    '{}'::jsonb,
    2
),
(
    'Selection any list',
    3,
    1,
    1,
    '{
        "place_filter_type": "any",
        "output_type": "list",
        "selection": "history_order"
    }'::jsonb,
    '{}'::jsonb,
    1
);
