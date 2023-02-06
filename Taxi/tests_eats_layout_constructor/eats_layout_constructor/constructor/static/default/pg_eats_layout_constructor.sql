insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'banners',
    'Widget template 1',
    '{"field_1": "value_1"}'::jsonb,
    '{"field_2": "value_2"}'::jsonb,
    '{"type": "object"}'::jsonb
),
(
    'places_carousel',
    'Widget template 2',
    '{"field_1": "value_1"}'::jsonb,
    '{"field_2": "value_2"}'::jsonb,
    '{"type": "object"}'::jsonb
),
(
   'popup_banner',
   'Popup banner',
   '{}'::jsonb,
   '{}'::jsonb,
   '{}'::json
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
    'nevladov',
    '2020-05-25T08:00:00+0000'
),
(
    nextval('constructor.layouts_id_seq'),
    'Layout 2',
    'layout_2',
    'nevladov',
    '2020-05-25T09:00:00+0000'
),
(
    100,
    'Layout 100',
    'layout_100',
    'nevladov',
    '2020-05-25T09:00:00+0000'
),
(
    101,
    'Layout 101',
    'layout_101',
    'nevladov',
    '2020-05-25T09:00:00+0000'
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
    2,
     '{"field_1": "value_3"}'::jsonb,
     '{"field_1": "value_3"}'::jsonb
),
(
    nextval('constructor.layout_widgets_url_id_seq'),
    'Widget 2',
    1,
    2,
     '{"field_1": "value_3"}'::jsonb,
     '{"field_1": "value_3"}'::jsonb
);
