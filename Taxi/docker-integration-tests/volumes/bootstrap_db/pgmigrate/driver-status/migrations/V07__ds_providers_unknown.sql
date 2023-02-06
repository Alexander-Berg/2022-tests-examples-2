-- can only be done while ds.orders is still empty
TRUNCATE TABLE ds.providers RESTART IDENTITY CASCADE;

INSERT INTO ds.providers(name)
VALUES ('unknown'),
       ('park'),
       ('yandex'),
       ('upup'),
       ('formula'),
       ('offtaxi'),
       ('app');
