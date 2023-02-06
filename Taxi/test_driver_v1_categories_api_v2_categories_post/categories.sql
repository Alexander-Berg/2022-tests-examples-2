-- categories
INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('econom','yandex',NOW(),'{"taximeter_value": 1, "taximeter_sort_order": 1}'),
('child_tariff','yandex',NOW(),'{"taximeter_value": 2, "taximeter_sort_order": 2}');

INSERT INTO categories.car_categories(park_id, car_id, categories, updated_at, jdoc) VALUES
('park_0','car_0','{"econom"}',NOW(),'{}'),
('park_4','car_4','{"econom"}',NOW(),'{}'),
('park_11','car_11','{"econom","child_tariff"}',NOW(),'{}'),
('park_6','car_6','{"econom"}',NOW(),'{}');

INSERT INTO categories.park_categories(park_id, categories, updated_at, jdoc) VALUES
('park_3','{"econom"}',NOW(),'{}'),
('park_4','{"child_tariff"}',NOW(),'{}'),
('park_5','{"child_tariff"}',NOW(),'{}'),
('park_11','{"child_tariff"}',NOW(),'{}'),
('park_7','{"econom"}',NOW(),'{}');
