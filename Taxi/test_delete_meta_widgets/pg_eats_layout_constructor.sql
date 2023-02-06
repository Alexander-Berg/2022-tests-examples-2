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
       "action_extenders":["actions_info"],
       "meta_extenders":["meta_info"]
     }'::jsonb
 ),
 (
     'place_layout',
     'drop_some',
     'Drop some meta and actions',
     '{
       "order":["actions", "meta"],
       "action_extenders":["actions_info", "actions_promo"],
       "meta_extenders":["meta_rating", "meta_price_category"]
     }'::jsonb
 );

insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
   'places_carousel',
   'Widget template 2',
   '{}'::jsonb,
   '{}'::jsonb,
   '{"type": "object"}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author,
    created
)
values
(
    'Layout 1',
    'layout_1',
    'mazgutov',
    '2020-05-25T08:00:00+0000'
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
    'Widget 1',
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb,
    1
)
