insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_carousel',
    'Places Carousel',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Places List',
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    id,
    name,
    slug,
    author
)
values
(
    1,
    'Top Layout',
    'top_layout',
    'mazgutov'
),
(
    2,
    'Favourite & Samovyvoz Layout',
    'favourite_samovyvoz_layout',
    'mazgutov'
),
(
    3,
    'Samovyvoz Layout',
    'samovyvoz_layout',
    'mazgutov'
),
(
    4,
    'No Filters Layout',
    'no_filters',
    'mazgutov'
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
    'Promo Carousel for top layout',
    1,
    1,
    1,
     '{"carousel": "promo"}'::jsonb,
     '{"title": "Promo for top layout"}'::jsonb
),
(
    'New Carousel for favourite_samovyvoz layout',
    2,
    1,
    2,
     '{"carousel": "new"}'::jsonb,
     '{"title": "New for favourite_samovyvoz layout"}'::jsonb
),
(
    'Open places for samovyvoz layout',
    3,
    2,
    3,
     '{"place_filter_type": "open"}'::jsonb,
     '{"title": "Open for favourite layout"}'::jsonb
),
(
    'Closed place without filters',
    4,
    2,
    4,
     '{"place_filter_type": "closed"}'::jsonb,
     '{"title": "Closed for all"}'::jsonb
);
