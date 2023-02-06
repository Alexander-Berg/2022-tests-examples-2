INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('econom','yandex',NOW(),'{"taximeter_value": 1, "taximeter_sort_order": 1}'),
('scooters','yandex',NOW(),'{"taximeter_value": 4, "taximeter_sort_order": 2}'),
('express','yandex',NOW(),'{"taximeter_value": 8, "taximeter_sort_order": 3}'),
('comfortplus','yandex',NOW(),'{"taximeter_value": 16, "taximeter_sort_order": 4}');

INSERT INTO categories.car_categories(park_id, car_id, categories, updated_at, jdoc) VALUES
('park_group_0','car_group_0','{"econom"}',NOW(),'{}'),
('park_group_0','car_group_1','{}',NOW(),'{}'),
('park_group_1','car_group_1','{"econom","comfortplus"}',NOW(),'{}'),
('park_group_2','car_group_2','{"econom","comfortplus","scooters","express"}',NOW(),'{}');
