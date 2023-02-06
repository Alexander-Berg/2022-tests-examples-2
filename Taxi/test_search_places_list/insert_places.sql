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
    address_comment,
    contacts,
    working_intervals,
    allowed_couriers_types)
VALUES
    (10, '2020-10-10T05:05:05+03:00', '2020-10-10T05:05:05+03:00', 'slug10', true, 'Название10', 100,
        'native', 'zapravki', '2020-10-10T05:05:05+03:00',
        ARRAY['cash','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
        (1,'slug','name', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
        (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
        ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
        ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
        point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
        '{"shown":4.83, "users":4.5, "admin":1.0, "count":200}', '{}',
        '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
        '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
        '{"popular": 1, "weight": 1, "wizard": 1}', 'test_comment', '[{"personal_phone_id":"123", "extension":"123", "type":"official"}]',
     ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[]),
    (11, '2020-10-10T05:05:05+03:00', '2020-10-10T05:05:05+03:00', 'slug11', false, 'Название11', 101,
        'native', 'zapravki', '2020-10-10T05:05:05+03:00',
        ARRAY['cash','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
        (1,'slug','name', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
        (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
        ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
        ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
        point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
        '{"shown":4.83, "users":4.5, "admin":1.0, "count":200}', '{}',
        '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
        '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
        '{"popular": 1, "weight": 1, "wizard": 1}', 'test_comment', '[{"personal_phone_id":"123", "extension":"123", "type":"official"}]',
     ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[]),
    (20, '2020-10-17T05:05:05+03:00', '2020-10-20T05:05:05+03:00', 'slug20', true, 'Название20', 102,
        'native', 'zapravki', '2020-10-10T05:05:05+03:00',
        ARRAY['cash','taxi']::storage.place_payment_method[], ARRAY[]::storage.place_gallery[],
        (1,'slug','name', 'aspect_fit')::storage.place_brand_v2, ('city','short')::storage.place_address,
        (1,'name','code',('code','sign')::storage.place_country_currency)::storage.place_country,
        ARRAY[]::storage.place_category[], ARRAY[]::storage.place_quick_filter[],
        ARRAY[]::storage.place_quick_filter[], (1,'{1,2}'::bigint[],'zone','name')::storage.place_region,
        point(3,4), (1,'name',0.5)::storage.place_price_category, 123,
        '{"shown":4.83, "users":4.5, "admin":1.0, "count":200}', '{}',
        '{"fast_food": true, "ignore_surge": false, "supports_preordering": false}',
        '{"preparation": 300, "extra_preparation": 300, "average_preparation": 300}',
        '{"popular": 1, "weight": 1, "wizard": 1}', NULL, NULL,
     ARRAY[]::storage.working_interval[], ARRAY[]::storage.delivery_zone_couriers_type[]);