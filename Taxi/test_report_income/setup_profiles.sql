INSERT INTO profiles (id, inn, status, park_id, driver_id, created_at, modified_at)
VALUES ('smz1', 'inn1', 'confirmed', 'p1', 'c1', NOW(), NOW()),
       ('smz2', 'inn2', 'confirmed', 'p2', 'c2', NOW(), NOW()),
       ('smz3', 'inn3', 'confirmed', 'p3', 'c3', NOW(), NOW()),
       ('smz4', 'inn4', 'confirmed', 'p4', 'c4', NOW(), NOW()),
       ('smz5', 'inn5', 'confirmed', 'p5', 'c5', NOW(), NOW()),
       ('smz7', 'inn7', 'confirmed', 'p7', 'c7', NOW(), NOW()),
       ('smz8', 'inn8', 'confirmed', 'p8', 'c8', NOW(), NOW()),
       ('smz9', 'inn9', 'confirmed', 'p9', 'c9', NOW(), NOW()),
       ('smz10', 'inn10', 'confirmed', 'p10', 'c10', NOW(), NOW()),
       ('smz11', 'inn11', 'confirmed', 'p11', 'c11', NOW(), NOW()),
       ('smz12', 'inn12', 'rejected', 'p12', 'c12', NOW(), NOW());

INSERT INTO se.nalogru_phone_bindings (phone_pd_id, inn_pd_id, status)
VALUES ('phone1_pd_id', 'inn1_pd_id', 'COMPLETED'),
       ('phone2_pd_id', 'inn2_pd_id', 'COMPLETED'),
       ('phone3_pd_id', 'inn3_pd_id', 'COMPLETED'),
       ('phone4_pd_id', 'inn4_pd_id', 'COMPLETED'),
       ('phone5_pd_id', 'inn5_pd_id', 'COMPLETED'),
       ('phone6_pd_id', 'inn6_pd_id', 'COMPLETED'),
       ('phone7_pd_id', 'inn7_pd_id', 'COMPLETED'),
       ('phone8_pd_id', 'inn8_pd_id', 'COMPLETED'),
       ('phone9_pd_id', 'inn9_pd_id', 'COMPLETED'),
       ('phone10_pd_id', 'inn10_pd_id', 'COMPLETED'),
       ('phone11_pd_id', 'inn11_pd_id', 'COMPLETED'),
       ('phone12_pd_id', 'inn12_pd_id', 'FAILED');
