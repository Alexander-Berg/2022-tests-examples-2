INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('Y','yandex',NOW(),'{}'),
('YY','yandex',NOW(),'{}'),
('A','a',NOW(),'{}'),
('AA','a',NOW(),'{}'),
('B','b',NOW(),'{}'),
('BB','b',NOW(),'{}');

INSERT INTO categories.park_categories
(park_id, categories, updated_at, jdoc) VALUES
('a0','{"Y","A"}',NOW()+'-3 hour','{}'),
('a1','{"A","B"}',NOW()+'-1 hour','{}'),
('a2','{}',NOW()+'-1 hour','{}'),
('a3','{"Y","A","B","YY","AA","BB"}',NOW()+'-1 hour','{}')
