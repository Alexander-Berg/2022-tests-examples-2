insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values (
    'places_carousel',
    'Widget template 1',
    '{"carousel": "new", "min_count": 10}'::jsonb,
    '{"title": "Бла бла бла"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 2',
    '{"low": 2, "place_filter_type": "open"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_carousel',
    'Widget template 3',
    '{"carousel": "advertisements"}'::jsonb,
    '{"title": "Реклама"}'::jsonb,
    '{}'::jsonb
),
(
    'places_carousel',
    'Widget template 4',
    '{"carousel": "pickup"}'::jsonb,
    '{"title": "Самовывоз"}'::jsonb,
    '{}'::jsonb
),
(
    'places_list',
    'Widget template 5',
    '{"place_filter_type": "advertisements"}'::jsonb,
    '{"title": "Реклама"}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Widget template 6',
    '{"place_filter_type": "open", "output_type": "carousel"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_carousel',
    'Widget template 7',
    '{"carousel": "open"}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Widget template 8',
    '{"place_filter_type": "place-menu-category", "output_type": "carousel", "place_menu_category_tag": "my_category_tag"}'::jsonb,
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
    'Layout 1',
    'layout_1',
    'nevladov'
),
(
    'Layout 2',
    'layout_2',
    'nevladov'
),
(
    'Layout 3',
    'layout_3',
    'nevladov'
),
(
    'Layout 4',
    'layout_4',
    'nevladov'
),
(
    'Catalog required',
    'source_required',
    'mazgutov'
),
(
    'Catalog not required',
    'source_not_required',
    'mazgutov'
),
(
    'Layout advertisements',
    'layout_advertisements',
    'udalovmax'
),
(
    'Layout with pickup carousel',
    'with_pickup_carousel',
    'nk2ge5k'
),
(
    'Layout with place_list advertisment',
    'with_place_list_ads',
    'egor-sorokin'
),
(
    'Layout with carousel 30 min delivery',
    'delivery_time_and_delivery_type',
    'user'
),
(
    'Layout place menu category block',
    'place_menu_category_layout',
    'user'
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
    'Widget 1',
    1,
    1,
    1,
     '{"carousel": "promo", "min_count": 5}'::jsonb,
     '{"title": "Акции и новинки"}'::jsonb
),
(
    'Widget 2',
    2,
    1,
    1,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 3',
    3,
    1,
    2,
     '{}'::jsonb,
     '{}'::jsonb
),
(
    'Widget 4',
    4,
    1,
    2,
     '{"carousel": "taxi-delivery", "min_count": 5}'::jsonb,
     '{"title": "Теперь доедет"}'::jsonb
),
(
    'Widget 5',
    5,
    2,
    4,
     '{
        "high": 2,
        "low": 0,
        "exclude_businesses": ["shop", "store"]
      }'::jsonb,
     '{"title": "Два первых ресторана"}'::jsonb
),
(
    'Widget 6',
    6,
    2,
    4,
     '{
        "high": 4,
        "exclude_businesses": ["shop", "store"]
      }'::jsonb,
     '{"title": "Два следующих ресторана"}'::jsonb
),
(
    'Widget 7',
    7,
    2,
    4,
     '{
        "low": 4,
        "exclude_businesses": ["shop", "store"]
      }'::jsonb,
     '{"title": "Все оставшиеся рестораны"}'::jsonb
),
(
    'required',
    8,
    2,
    5,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'not_required',
    9,
    2,
    6,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'advertisements',
    10,
    3,
    7,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'with_pickup_carousel',
    11,
    4,
    8,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'Widget 8',
    12,
    5,
    9,
    '{"low": 0,"high": 1}'::jsonb,
    '{"title": "Реклама"}'::jsonb
),
(
    'Widget 9',
    13,
    5,
    9,
    '{"low": 1,"high": 2}'::jsonb,
    '{"title": "Реклама"}'::jsonb
),
(
  '30 min Carousel',
  14,
  6,
  10,
  '{"max_delivery_time": 30, "delivery_type": "native", "sort_type": "fast_delivery"}'::jsonb,
  '{"title": "Доставка за 30 минут"}'::jsonb
),
(
  '30 min Carousel',
  15,
  7,
  10,
  '{"max_delivery_time": 30, "delivery_type": "native", "sort_type": "fast_delivery"}'::jsonb,
  '{"title": "Доставка за 30 минут"}'::jsonb
),
(
  'Place Menu Category',
  16,
  8,
  11,
  '{}'::jsonb,
  '{"title": "Переход в категорию"}'::jsonb
);
