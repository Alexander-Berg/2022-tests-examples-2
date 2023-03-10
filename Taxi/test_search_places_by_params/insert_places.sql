INSERT INTO storage.places (
    id,
    created_at,
    updated_at,
    slug,
    enabled,
    name,
    revision,
    type,
    business,
    launched_at,
    payment_methods,
    gallery,
    brand,
    address,
    country,
    categories,
    quick_filters,
    wizard_quick_filters,
    region,
    location,
    price_category,
    assembly_cost,
    rating,
    extra_info,
    features,
    timing,
    sorting,
    working_intervals,
    allowed_couriers_types,
    revision_id)
VALUES
(55, '2021-01-29T14:50:12.017363+00:00', '2021-01-29T14:50:12.017363+00:00', 'slug55', true, 'Название55', 1,
    'native', 'restaurant', '2021-01-29T14:50:12.017363+00:00',
    ARRAY['cash', 'payture', 'apple_pay','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
    (5,'brand_slug5','brand_name5', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
    (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
    ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
    ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
    point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
    '{"shown":4.685, "users":4.685, "admin":1.0, "count":200}', '{}',
    '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
    '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
    '{"popular": 1, "weight": 1, "wizard": 1}',
    ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[], 1000),
(56, '2021-01-29T14:50:12.017363+00:00', '2021-01-29T14:50:12.017363+00:00', 'slug56', false, 'Название56', 520,
    'native', 'restaurant', '2021-01-29T14:50:12.017363+00:00',
    ARRAY['cash', 'payture', 'apple_pay','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
    (6,'brand_slug6','brand_name6', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
    (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
    ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
    ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
    point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
    '{"shown":4.685, "users":4.685, "admin":1.0, "count":200}', '{}',
    '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
    '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
    '{"popular": 1, "weight": 1, "wizard": 1}',
    ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[], 1002),
(57, '2021-01-29T14:50:12.017363+00:00', '2021-01-29T14:50:12.017363+00:00', 'slug57', true, 'Название57', 401,
    'native', 'restaurant', '2021-01-29T14:50:12.017363+00:00',
    ARRAY['cash', 'payture', 'apple_pay','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
    (6,'brand_slug6','brand_name6', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
    (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
    ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
    ARRAY[]::storage.place_quick_filter[], (8,'{9,10}'::bigint[],'zone','name')::storage.place_region,
    point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
    '{"shown":4.685, "users":4.685, "admin":1.0, "count":200}', '{}',
    '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
    '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
    '{"popular": 1, "weight": 1, "wizard": 1}',
    ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[], 1004),
(58, '2021-01-29T14:50:12.017363+00:00', '2021-01-29T14:50:12.017363+00:00', 'slug58', true, 'Название58', 300,
    'native', 'restaurant', '2021-01-29T14:50:12.017363+00:00',
    ARRAY['cash', 'payture', 'apple_pay','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
    (6,'brand_slug6','brand_name6', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
    (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
    ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
    ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
    point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
    '{"shown":4.685, "users":4.685, "admin":1.0, "count":200}', '{}',
    '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
    '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
    '{"popular": 1, "weight": 1, "wizard": 1}',
    ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[], 1004)
