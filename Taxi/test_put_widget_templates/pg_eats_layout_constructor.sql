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
 ),
 (
     'place_layout',
     'empty',
     'Empty',
     '{
       "order":[],
       "action_extenders":[],
       "meta_extenders":[]
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
   '{"field_1": "value_1"}'::jsonb,
   '{"field_2": "value_2"}'::jsonb,
   '{"type": "object"}'::jsonb
),
(
   2,
   'places_carousel',
   'Widget template 2',
   '{"field_1": "value_1"}'::jsonb,
   '{"field_2": "value_2"}'::jsonb,
   '{"type": "object"}'::json
),
(
   3,
   'places_carousel',
   'Widget template 3',
   '{}'::jsonb,
   '{}'::jsonb,
   '{}'::jsonb
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
    nextval('constructor.layouts_id_seq'),
    'Layout 1',
    'layout_1',
    'mazgutov',
    '2020-05-25T08:00:00+0000'
);

insert into constructor.layout_widgets (
    url_id,
    name,
    widget_template_id,
    layout_id,
    meta,
    payload
)
values
(
    nextval('constructor.layout_widgets_url_id_seq'),
    'Widget 1',
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb
);
