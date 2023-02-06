insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
    'places_list',
    'Places List Template',
    '{"place_filter_type": "open"}'::jsonb,
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
    'Simple layout',
    'test_place_layout',
    'mazgutov'
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
      "action_extenders":["actions_repeat_order"],
      "meta_extenders":["meta_rating", "meta_price_category", "meta_info"]
     }'::jsonb
),
(
     'place_layout',
     'drop_some',
     'Drop some meta and actions',
     '{
       "order":["actions", "meta"],
       "action_extenders":["actions_repeat_order"],
       "meta_extenders":["meta_rating", "meta_price_category"]
     }'::jsonb
),
(
     'place_layout',
     'no_actions',
     'Drop all actions',
     '{
       "order":["meta"],
       "action_extenders":[],
       "meta_extenders":["meta_rating", "meta_price_category"]
     }'::json
);


insert into constructor.layout_widgets (
    name,
    widget_template_id,
    layout_id,
    meta,
    payload,
    meta_widget
)
values
(
    'Places List 1',
    1,
    1,
    '{"meta_widget":"order_existing"}'::jsonb,
    '{}'::jsonb,
    1
),
(
    'Places List 2',
    1,
    1,
    '{"meta_widget":"drop_some"}'::jsonb,
    '{}'::jsonb,
    2
),
(
    'Places List 3',
    1,
    1,
    '{"meta_widget":"no_actions"}'::jsonb,
    '{}'::jsonb,
    3
);
