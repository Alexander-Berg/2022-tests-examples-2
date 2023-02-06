insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
) values (
    'places_carousel',
    'Widget template 1',
    '{}'::jsonb,
    '{"title": "Карусель"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 2',
    '{}'::jsonb,
    '{"title": "Список"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
) values (
    'Layout 1',
    'layout_1',
    'user'
);

insert into constructor.layout_widgets (
    name,
    widget_template_id,
    layout_id,
    meta,
    payload
) values (
    'Layout 1 Widget 1',
    1,
    1,
     '{"carousel": "new", "min_count": 1}'::jsonb,
     '{"background_color_dark": "#FFFFFF"}'::jsonb
),
(
    'Layout 1 Widget 2',
    2,
    1,
     '{"low": 0, "place_filter_type": "open"}'::jsonb,
     '{"background_color_dark": ""}'::jsonb
);
