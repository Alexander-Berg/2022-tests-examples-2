INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('Y','yandex',NOW(),'{}'),
('YY','yandex',NOW(),'{}'),
('A','a',NOW(),'{}'),
('AA','a',NOW(),'{}'),
('B','b',NOW(),'{}'),
('BB','b',NOW(),'{}');

INSERT INTO categories.car_categories
(park_id, car_id, categories, updated_at, jdoc) VALUES
('a0','b00','{"Y","A"}',NOW()+'-3 hour','{}'),
('a1','b10','{"A","B"}',NOW()+'-1 hour','{}'),
('a1','b11_empty','{}',NOW()+'-1 hour','{}'),
('a1','b12','{"Y","A","B","YY","AA","BB"}',NOW()+'-1 hour','{}')

