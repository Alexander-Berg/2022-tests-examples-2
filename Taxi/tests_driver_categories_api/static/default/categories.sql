-- categories
INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('business','yandex',NOW(),'{"restriction_value":64,"taximeter_value":2,"old_client_name":"comfort","taximeter_name":"comfort","db_cars_name":"comfort"}'),
('business2','yandex',NOW(),'{"restriction_value":4096,"taximeter_value":512,"old_client_name":"comfortplus","taximeter_name":"comfortplus","db_cars_name":"comfort_plus"}'),
('cargo','yandex',NOW(),'{"restriction_value":67108864,"taximeter_value":33554432,"park_city_country_feature_config":"TAXIMETER_CARGO_CATEGORY_SETTINGS"}'),
('child_tariff','yandex',NOW(),'{"restriction_value":262144,"taximeter_value":16384}'),
('comfortplus','yandex',NOW(),'{"restriction_value":4096,"taximeter_value":512,"old_client_name":"comfortplus","taximeter_name":"comfortplus","db_cars_name":"comfort_plus"}'),
('courier','yandex',NOW(),'{"restriction_value":268435456,"taximeter_value":268435456,"park_feature_config":"TAXIMETER_COURIER_CATEGORY_SETTINGS"}'),
('demostand','yandex',NOW(),'{"taximeter_value":524288,"park_feature_config":"TAXIMETER_DEMOSTAND_CATEGORY_SETTINGS"}'),
('econom','yandex',NOW(),'{"restriction_value":32,"taximeter_value":1}'),
('eda','yandex',NOW(),'{"restriction_value":536870912,"taximeter_value":536870912,"park_feature_config":"TAXIMETER_EDA_CATEGORY_SETTINGS"}'),
('express','yandex',NOW(),'{"restriction_value":16384,"taximeter_value":1024,"park_city_country_feature_config":"TAXIMETER_EXPRESS_CATEGORY_SETTINGS"}'),
('lavka','yandex',NOW(),'{"restriction_value":1073741824,"taximeter_value":1073741824,"park_feature_config":"TAXIMETER_LAVKA_CATEGORY_SETTINGS"}'),
('limousine','taximeter',NOW(),'{"taximeter_value":16,"park_city_country_feature_config":"TAXIMETER_LIMOUSINE_CATEGORY_SETTINGS"}'),
('maybach','yandex',NOW(),'{"restriction_value":1048576,"taximeter_value":262144}'),
('minibus','taximeter',NOW(),'{"taximeter_value":256}'),
('minivan','yandex',NOW(),'{"restriction_value":1024,"taximeter_value":8,"old_client_name":"miniven"}'),
('mkk','yandex',NOW(),'{"taximeter_value":65536,"is_hidden":true}'),
('mkk_antifraud','yandex',NOW(),'{"taximeter_value":134217728,"is_hidden":true,"park_city_country_feature_config":"TAXIMETER_MKK_ANTIFRAUD_CATEGORY_SETTINGS"}'),
('night','yandex',NOW(),'{"restriction_value":134217728,"taximeter_value":67108864,"is_hidden":true,"park_city_country_feature_config":"TAXIMETER_NIGHT_CATEGORY_SETTINGS"}'),
('park_vip','taximeter',NOW(),'{"taximeter_value":32,"taximeter_name":"vip","db_cars_name":"vip"}'),
('personal_driver','yandex',NOW(),'{"restriction_value":33554432,"taximeter_value":16777216,"park_city_country_feature_config":"TAXIMETER_PERSONAL_DRIVER_CATEGORY_SETTINGS"}'),
('pool','yandex',NOW(),'{"taximeter_value":2048,"park_city_country_feature_config":"TAXIMETER_POOL_CATEGORY_SETTINGS"}'),
('premium_suv','yandex',NOW(),'{"restriction_value":8388608,"taximeter_value":4194304,"park_city_country_feature_config":"TAXIMETER_PREMIUM_SUV_CATEGORY_SETTINGS"}'),
('premium_van','yandex',NOW(),'{"restriction_value":4194304,"taximeter_value":2097152,"park_city_country_feature_config":"TAXIMETER_PREMIUM_VAN_CATEGORY_SETTINGS"}'),
('promo','yandex',NOW(),'{"restriction_value":2097152,"taximeter_value":1048576,"park_city_country_feature_config":"TAXIMETER_PROMO_CATEGORY_SETTINGS"}'),
('scooters','yandex',NOW(),'{"taximeter_value":-2147483648,"restriction_value":-2147483648,"park_feature_config":"TAXIMETER_SCOOTERS_CATEGORY_SETTINGS"}'),
('selfdriving','yandex',NOW(),'{"taximeter_value":131072,"park_feature_config":"TAXIMETER_SELFDRIVING_CATEGORY_SETTINGS"}'),
('standart','yandex',NOW(),'{"restriction_value":131072,"taximeter_value":8192,"old_client_name":"standard","taximeter_name":"standard"}'),
('start','yandex',NOW(),'{"restriction_value":65536,"taximeter_value":4096}'),
('suv','yandex',NOW(),'{"restriction_value":16777216,"taximeter_value":8388608,"park_city_country_feature_config":"TAXIMETER_SUV_CATEGORY_SETTINGS"}'),
('trucking','taximeter',NOW(),'{"taximeter_value":64}'),
('ultimate','yandex',NOW(),'{"restriction_value":524288,"taximeter_value":32768}'),
('universal','yandex',NOW(),'{"restriction_value":8192,"taximeter_value":128,"old_client_name":"touring","taximeter_name":"wagon","db_cars_name":"wagon"}'),
('vip','yandex',NOW(),'{"restriction_value":128,"taximeter_value":4,"old_client_name":"bussines","taximeter_name":"business","db_cars_name":"business"}');

-- driver restrictions
INSERT INTO categories.driver_restrictions(park_id,driver_id,categories,updated_at,jdoc) VALUES
('park_0','driver_0','{}',NOW(),'{}'),

('park_0','driver_2',ARRAY[
    'business',
    'business2',
    'cargo',
    'child_tariff',
    'comfortplus',
    'courier',
    'econom',
    'eda',
    'express',
    'lavka',
    'maybach',
    'minivan',
    'night',
    'personal_driver',
    'premium_suv',
    'premium_van',
    'promo',
    'scooters',
    'standart',
    'start',
    'suv',
    'ultimate',
    'universal',
    'vip'
],NOW(),'{}'),

('park_1','driver_0',ARRAY[
    'child_tariff',
    'personal_driver',
    'premium_suv',
    'premium_van',
    'promo',
    'standart',
    'start',
    'suv',
    'ultimate',
    'universal',
    'vip'
],NOW(),'{}'),

('park_3','driver_0',ARRAY[
    'business',
    'standart',
    'universal',
    'vip'
],NOW(),'{}'),

('park_5','driver_0',ARRAY['comfortplus'],NOW(),'{}');

-- car categories
INSERT INTO categories.car_categories(park_id,car_id,categories,updated_at,jdoc) VALUES
('park_0','car_1',(SELECT array_agg(c.name) FROM categories.categories AS c WHERE c.name != 'child_tariff'),NOW(),'{}'),

('park_1','car_1',ARRAY[
    'business',
    'business2',
    'comfortplus',
    'courier',
    'demostand',
    'econom',
    'express',
    'limousine',
    'maybach',
    'minibus',
    'suv',
    'ultimate',
    'vip'
],NOW(),'{}'),

('park_2','car_0',(SELECT array_agg(c.name) FROM categories.categories AS c WHERE c.name != 'child_tariff'),NOW(),'{}'),

('park_3','car_0',ARRAY[
    'business',
    'comfortplus',
    'park_vip',
    'universal',
    'vip'
],NOW(),'{}');

-- park categories
INSERT INTO categories.park_categories(park_id,categories,updated_at,jdoc) VALUES
('park_0',(SELECT array_agg(c.name) FROM categories.categories AS c),NOW(),'{}'),

('park_1',ARRAY[
    'child_tariff',
    'comfortplus',
    'suv',
    'ultimate',
    'universal',
    'vip'
],NOW(),'{}'),

('park_3',ARRAY[
    'business',
    'standart',
    'universal',
    'vip'
],NOW(),'{}'),

('park_5',ARRAY['comfortplus'],NOW(),'{}'),

('park_6',ARRAY['vip'],NOW(),'{}');
