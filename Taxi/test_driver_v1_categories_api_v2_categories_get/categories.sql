-- categories
INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('econom','yandex',NOW(),'{"taximeter_value": 1}'),
('child_tariff','yandex',NOW(),'{"taximeter_value": 2, "taximeter_sort_order": 1}');

INSERT INTO categories.car_categories(park_id, car_id, categories, updated_at, jdoc) VALUES
('park_0','car_0','{"econom"}',NOW(),'{}'),
('park_1','car_1','{"econom"}',NOW(),'{}'),
('park_2','car_2','{"econom"}',NOW(),'{}'),
('park_coord_city','car_3','{"econom"}',NOW(),'{}');
