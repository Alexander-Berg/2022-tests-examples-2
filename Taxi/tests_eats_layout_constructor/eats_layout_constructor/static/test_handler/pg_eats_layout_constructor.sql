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
    'Widget template 1',
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
    'open places',
    'layout_1',
    'udalovmax'
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload
)
values
(
    'open places',
    1,
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb
);
