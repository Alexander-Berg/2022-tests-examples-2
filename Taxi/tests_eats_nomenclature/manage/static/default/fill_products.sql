-- Insert products
insert into eats_nomenclature.brands (id) values (777);

insert into eats_nomenclature.measure_units (id, value, name)
values (1, 'GRM','г'),
       (2, 'KGRM','кг'),
       (3, 'LT','л'),
       (4, 'MLT','мл');

insert into eats_nomenclature.products (origin_id, name, brand_id, public_id, measure_unit_id, measure_value, quantum, is_catch_weight)
values ('item_origin_1', 'item_1', 777, '11111111111111111111111111111111', 1, 150, 0, false),
       ('item_origin_2', 'item_2', 777, '22222222222222222222222222222222', 2, 2000, 0.4, true),
       ('item_origin_3', 'item_3', 777, '33333333333333333333333333333333', 3, 5, 0, false),
       ('item_origin_4', 'item_4', 777, '44444444444444444444444444444444', null, null, 0, false),
       ('item_origin_5', 'item_5', 777, '55555555555555555555555555555555', null, null, 0, false);

insert into eats_nomenclature.product_types (value_uuid, value)
values ('value_uuid1', 'value1'),
       ('value_uuid2', 'value2'),
       ('value_uuid3', 'value3');

insert into eats_nomenclature.pictures (url, processed_url, needs_subscription)
values ('url_1', null, True),
       ('url_2', 'processed_url_2', False),
       ('url_3', null, False);
