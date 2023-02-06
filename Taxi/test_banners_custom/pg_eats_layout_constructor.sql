insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
    'banners',
    'Banners',
    '{"format":"classic"}'::jsonb,
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
    'Banners Custom',
    'banners_custom_layout',
    'user'
);

insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'banners_custom',
     'full_wigth',
     'Full wight banner meta widget',
     '{
       "width": "full"
     }'::jsonb
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload,
    meta_widget,
    meta_widget_experiment_name
)
values
(
    'Generic',
    1,
    1,
    1,
    '{"format": "classic"}'::jsonb,
    '{"title": "Баннер как было раньше"}'::jsonb,
    NULL,
    NULL
),
(
    'With meta widget',
    2,
    1,
    1,
    '{"format": "classic"}'::jsonb,
    '{"title": "Баннер с новым полем"}'::jsonb,
    1,
    NULL
);
