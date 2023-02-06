INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('A','yandex',NOW(),'{}'),
('B','yandex',NOW(),'{}'),
('C','yandex',NOW(),'{}'),
('D','yandex',NOW(),'{}'),
('E','yandex',NOW(),'{}'),
('a','other',NOW(),'{}');

INSERT INTO categories.car_categories
(park_id, car_id, categories, updated_at, jdoc) VALUES
('a0','b00','{"A","B","a"}',NOW(),'{}'),
('a1','b10','{"C","a","D"}',NOW(),'{}'),
('a1','b11_empty','{}',NOW(),'{}'),
('a1','b12','{"E"}',NOW(),'{}')

