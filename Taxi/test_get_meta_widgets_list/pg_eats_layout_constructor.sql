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
