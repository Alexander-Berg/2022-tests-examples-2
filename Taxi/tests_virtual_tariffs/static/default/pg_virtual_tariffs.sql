INSERT INTO virtual_tariffs.tariff (id, description, revision)
VALUES ('econom_pj', 'Description1', nextval('virtual_tariffs.tariff_revision')),
       ('comfort_pj', 'Description2', nextval('virtual_tariffs.tariff_revision'));

INSERT INTO virtual_tariffs.tariff_coverage (tariff_id, corp_client_id, zone_id, class_id)
VALUES ('econom_pj', 'b04a64bb1d0147258337412c01176fa1', 'moscow', null),
       ('econom_pj', '01234567890123456789012345678912', 'moscow', 'comfort'),
       ('comfort_pj', null, 'moscow', 'business');

INSERT INTO virtual_tariffs.special_requirement(id, description, revision, updated)
VALUES ('empty', 'Пустое спецтребование', 1, '2018-12-28 00:00:00+0000'::timestamptz),
       ('food_delivery', 'Способен доставлять еду', 20, '2018-12-28 00:00:00+0000'::timestamptz),
       ('good_driver', 'Хороший водитель', 22, '2020-01-01 11:59:50+0000'::timestamptz);

SELECT setval('virtual_tariffs.special_requirement_revision', 22, true);

INSERT INTO virtual_tariffs.requirement (field, operation, arguments, special_requirement_id)
VALUES ('tags', 'contains', ARRAY ['food_box'], 'food_delivery'),
       ('rating', 'over', ARRAY ['4.95'], 'food_delivery');

INSERT INTO virtual_tariffs.tariff_special_requirement (tariff_id, special_requirement_id)
VALUES ('econom_pj', 'food_delivery'), ('comfort_pj', 'good_driver');
