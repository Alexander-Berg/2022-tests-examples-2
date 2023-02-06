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
),
(
    'places_carousel',
    'Widget template 2',
    '{"carousel": "advertisements"}'::jsonb,
    '{"title": "Реклама"}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Layout with meta widget from field',
    'layout_1',
    'nk2ge5k'
),
(
    'Layout with meta widget from experiment',
    'layout_2',
    'nk2ge5k'
),
(
    'Layout with invalid meta widget experiment',
    'layout_3',
    'nk2ge5k'
),
(
    'Layout with unknown meta widget experiment',
    'layout_4',
    'nk2ge5k'
),
(
    'Layout with ads carousel and ads meta',
    'layout_5',
    'udalovmax'
);


insert into constructor.meta_widgets (
    type,
    slug,
    name,
    settings
) values (
     'place_layout',
     'first',
     'First meta widget',
     '{
       "order":["actions"],
       "action_extenders":["actions_promo"],
       "meta_extenders":[]
     }'::jsonb
),
(
     'place_layout',
     'second',
     'Second meta widget',
     '{
       "order":["meta"],
       "action_extenders":[],
       "meta_extenders":["meta_price_category"]
     }'::jsonb
),
(
     'place_layout',
     'advertisements',
     'Advertisements meta widget',
     '{
       "order":["meta"],
       "action_extenders":[],
       "meta_extenders":["meta_advertisements", "meta_price_category"]
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
) values (
    'Meta widget form field',
    1,
    1,
    1, /* layout_1 */
     '{}'::jsonb,
     '{}'::jsonb,
    1,
    NULL
),
(
    'Meta widget from experiment',
    2,
    1,
    2, /* layout_2 */
     '{}'::jsonb,
     '{}'::jsonb,
    1,
    'meta_widget_experiment'
),
(
    'Invalid meta widget from experiment',
    3,
    1,
    3, /* layout_3 */
     '{}'::jsonb,
     '{}'::jsonb,
    1,
    'invalid_meta_widget_experiment'
),
(
    'Unknown meta widget from experiment',
    4,
    1,
    4, /* layout_4 */
     '{}'::jsonb,
     '{}'::jsonb,
    1,
    'unknown_meta_widget_experiment'
),
(
    'Advertisements meta widet',
    5,
    2,
    5, /* layout_5 */
     '{}'::jsonb,
     '{}'::jsonb,
    3,
    NULL
);
