INSERT INTO ds.app_families(name)
VALUES ('taximeter'),
       ('uberdriver');

INSERT INTO ds.blocked_reasons(name)
VALUES ('none'),
       ('by_driver'),
       ('fns_unbound'),
       ('driver_taximeter_disabled'),
       ('driver_balance_debt'),
       ('driver_blacklist'),
       ('car_blacklist'),
       ('driver_dkk'),
       ('driver_license_verification'),
       ('driver_sts'),
       ('driver_identity'),
       ('driver_biometry'),
       ('pending_park_order'),
       ('car_is_used');

INSERT INTO ds.providers(name)
VALUES ('unknown'),
       ('park'),
       ('yandex'),
       ('upup'),
       ('formula'),
       ('offtaxi'),
       ('app');
