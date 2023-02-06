insert into constructor.meta_widgets (
    id,
    type,
    slug,
    name,
    settings
) values (
     1,
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
     2,
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
    id,
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
   1,
   'banners',
   'Widget template 1',
   '{}'::jsonb,
   '{}'::jsonb,
   '{"type": "object"}'::jsonb
);

insert into constructor.layouts (
    id,
    name,
    slug,
    author,
    created
)
values
(
    1,
    'Layout 1',
    'layout_1',
    'coder',
    '2020-05-25T08:00:00+0000'
);

insert into constructor.layout_widgets (
    name,
    widget_template_id,
    meta_widget,
    layout_id,
    meta,
    payload
)
values
(
    'Widget 1',
    1,
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb
);
