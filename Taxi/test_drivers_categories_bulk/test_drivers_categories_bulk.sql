INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES
('econom','yandex',NOW(),'{ "o":"f"}'),
('business','b',NOW(),'{"o":"b"}'),
('child','c',NOW(),'{"optional":"c"}'),
('wagon','w',NOW(),'{}'),
('minibus','m',NOW(),'{}'),
('minivan','m',NOW(),'{}'),
('comfort','c',NOW(),'{}'),
('trucking','',NOW(),'{}'),
('vip','',NOW(),'{}'),
('comfort_plus','cp',NOW(),'{}'),
('limousine','l',NOW(),'{}'),
('pool','p',NOW(),'{}');

INSERT INTO categories.driver_restrictions
(driver_id, park_id, categories, updated_at, jdoc) VALUES
('driver1','park_1','{"econom","child","business"}',NOW()+'1 minute','{}'),
('driver2','park_1','{"minibus"}',NOW()+'2 minute','{}'),
('driver3','park_2','{"wagon","econom"}',NOW()+'3 minute','{}');

INSERT INTO categories.park_categories
(park_id, categories, updated_at, jdoc) VALUES
('park_1','{"business","econom","wagon","minibus","minivan","comfort_plus","limousine","pool"}',NOW()+'1 minute','{}'),
('park_2','{"child"}',NOW()+'2 minute','{}');

INSERT INTO categories.car_categories
(car_id, park_id, categories, updated_at, jdoc) VALUES
('car1','park_1','{"wagon","business","comfort","econom","trucking","vip","comfort_plus","limousine","pool"}',NOW()+'1 minute','{}'),
('car2','park_1','{"wagon","minibus","business","minivan","comfort","econom","trucking","vip","comfort_plus","limousine","pool"}',NOW()+'2 minute','{}'),
('car3','park_1','{"minivan","comfort","econom","trucking","vip","comfort_plus","limousine","pool"}',NOW()+'3 minute','{}');
