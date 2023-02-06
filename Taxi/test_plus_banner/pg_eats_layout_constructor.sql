insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'plus_banner',
    'Plus Banner Template',
    '{}'::jsonb,
    '{"title": "widget title"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Layout 1',
    'plus_layout',
    'nk2ge5k'
);

insert into constructor.layout_widgets (
    name,
    widget_template_id,
    layout_id,
    meta,
    payload
)
values
(
    'Widget 1',
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb
);
