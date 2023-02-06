-- categories
INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('child_tariff','yandex',NOW(),'{"restriction_value":262144,"taximeter_value":16384}'),
('courier','yandex',NOW(),'{"restriction_value":268435456,"taximeter_value":268435456,"park_feature_config":"TAXIMETER_COURIER_CATEGORY_SETTINGS"}'),
('econom','yandex',NOW(),'{"restriction_value":32,"taximeter_value":1}'),
('express','yandex',NOW(),'{"restriction_value":16384,"taximeter_value":1024,"park_city_country_feature_config":"TAXIMETER_EXPRESS_CATEGORY_SETTINGS"}'),
('night','yandex',NOW(),'{"restriction_value":134217728,"taximeter_value":67108864,"is_hidden":true,"park_city_country_feature_config":"TAXIMETER_NIGHT_CATEGORY_SETTINGS"}');

-- driver restrictions
INSERT INTO categories.driver_restrictions(park_id,driver_id,categories,updated_at,jdoc) VALUES
('park_66','driver_66',ARRAY[
    'econom',
    'night'
],NOW(),'{}'),
('park_66','driver_666',ARRAY[
    'econom',
    'courier'
],NOW(),'{}'),
('park_66','driver_6666',ARRAY[
    'econom'
],NOW(),'{}');

-- car categories
INSERT INTO categories.car_categories(park_id,car_id,categories,updated_at,jdoc) VALUES
('park_66','car_66',ARRAY[
    'courier',
    'econom',
    'express',
    'night'
],NOW(),'{}');

-- park categories
INSERT INTO categories.park_categories(park_id,categories,updated_at,jdoc) VALUES
('park_66',ARRAY[
    'courier',
    'econom',
    'express',
    'night'
],NOW(),'{}');
