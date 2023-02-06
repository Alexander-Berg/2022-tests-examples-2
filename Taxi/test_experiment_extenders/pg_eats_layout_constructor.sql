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
      "action_extenders":["actions_experiment_extender"],
      "meta_extenders":["meta_experiment_extender"]
     }'::jsonb
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
     '{}'::jsonb,
     '{}'::jsonb,
    1
);
