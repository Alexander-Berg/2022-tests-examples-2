INSERT INTO profiles (id, inn, status, park_id, driver_id, created_at, modified_at)
VALUES ('smz1', 'inn1', 'confirmed', 'p1', 'd1', NOW(), NOW()),
       ('smz2', 'inn2', 'confirmed', 'p2', 'd2', NOW(), NOW()),
       ('smz3', 'inn3', 'confirmed', 'p3', 'd3', NOW(), NOW()),
       ('smz4', 'inn4', 'confirmed', 'p4', 'd4', NOW(), NOW()),
       ('smz5', 'inn5', 'confirmed', 'p5', 'd5', NOW(), NOW()),
       ('smz7', 'inn7', 'confirmed', 'p7', 'd7', NOW(), NOW()),
       ('smz8', 'inn8', 'confirmed', 'p8', 'd8', NOW(), NOW()),
       ('smz9', 'inn9', 'confirmed', 'p9', 'd9', NOW(), NOW());

INSERT INTO se.nalogru_phone_bindings (phone_pd_id, inn_pd_id, status, exceeded_legal_income_year)
VALUES ('phone1_pd_id', 'inn1_pd_id', 'COMPLETED', NULL),
       ('phone2_pd_id', 'inn2_pd_id', 'COMPLETED', NULL),
       ('phone3_pd_id', 'inn3_pd_id', 'COMPLETED', NULL),
       ('phone4_pd_id', 'inn4_pd_id', 'IN_PROGRESS', NULL),
       ('phone5_pd_id', 'inn5_pd_id', 'COMPLETED', NULL),
       ('phone6_pd_id', 'inn6_pd_id', 'COMPLETED', NULL),
       ('phone7_pd_id', 'inn7_pd_id', 'COMPLETED', NULL),
       ('phone8_pd_id', 'inn8_pd_id', 'COMPLETED', NULL),
       ('phone9_pd_id', 'inn9_pd_id', 'COMPLETED', NULL);
