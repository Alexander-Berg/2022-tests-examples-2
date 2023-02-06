insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
) values (
    'experiments_widget',
    'experiments_widget template 1',
    '{}'::jsonb,
    '{"title": "Experiments"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
) values (
    'Layout for exps',
    'layout_with_experiments',
    'user'
);

insert into constructor.layout_widgets (
    name,
    widget_template_id,
    layout_id,
    meta,
    payload
) values (
    'Any name widget',
    1,
    1,
    '{"exp_name": "exp_id_1"}'::jsonb,
    '{"title":"Any name widget"}'::jsonb
);
