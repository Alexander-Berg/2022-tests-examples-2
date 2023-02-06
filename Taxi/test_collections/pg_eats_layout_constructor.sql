insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
) values (
    'places_collection',
    'Default List',
    '{"place_filter_type": "open", "output_type": "list"}'::jsonb,
    '{"title": "Default List"}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Custom List',
    '{"place_filter_type": "open", "output_type": "list"}'::jsonb,
    '{"title": "Custom List"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
) values (
    'Default Collection layout',
    'default_collection_layout',
    'user'
),(
    'Custom Collection layout',
    'custom_collection_layout',
    'user' 
);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
    'place_layout',
    'advertisements',
    'Advertisements meta widget',
    '{
    "order":["meta"],
    "action_extenders":[],
    "meta_extenders":["meta_advertisements"]
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
    'Default List',
    1,
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb,
    1
), (
    'Custom List',
    2,
    2,
    2,
    '{}'::jsonb,
    '{}'::jsonb,
   NULL
);
