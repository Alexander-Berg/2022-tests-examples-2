insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'place_layout',
     'order_existing',
     'Sample meta widget',
     '{
       "order":["actions", "meta"],
       "action_extenders":["actions_info"],
       "meta_extenders":["meta_info"]
     }'::jsonb
);

insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
) values (
   'places_collection',
   'Place collection 1',
   '{"field_1": "value_1"}'::jsonb,
   '{"field_2": "value_2"}'::jsonb,
   '{"type": "object"}'::json
);
