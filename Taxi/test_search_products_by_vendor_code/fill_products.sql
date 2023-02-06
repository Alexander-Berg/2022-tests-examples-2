-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1), (2);
insert into eats_nomenclature.places (id, slug) values (1, 'slug'), (2, 'new_slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (2, 2);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), 
       ('vendor_2', 'country_2'), 
       ('vendor_3', 'country_3'), 
       ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, volume_unit_id, volume_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 1.0, 1, 100, 1, 10, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', null),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 2, 200, 2, 20, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', null),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, 3, 300, null, null, null, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', null),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 1.0, 4, 400, null, null, null, true, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', null),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005', null),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006', null),
       ('item_origin_7', 'mno', 3, 3, 'item_7', 0.0, null, null, null, null, true, true, false, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', null),
       ('item_origin_8', 'mno', 3, 3, 'item_8', 0.0, null, null, null, null, true, true, false, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008', null),
       ('item_origin_9', 'abc', 1, 1, 'item_9', 1.0, 1, 100, 1, 10, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009', null),
       ('item_origin_10', 'mno', 3, 3, 'item_10', 0.0, null, null, null, null, true, true, false, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010', null);

alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from, force_unavailable_until, vendor_code)
values (1, 401, 'item_origin_1', 999, null, null, null, null, '123'),
       (1, 402, 'item_origin_2', 999, 999, 10, now(), null, '123'),
       (1, 403, 'item_origin_3', 99.9, 1000, 20, '2017-01-08 04:05:06', null, '234'),
       (1, 404, 'item_origin_4', 999, 1000, 30, '2037-01-08', null, null),
       (1, 405, 'item_origin_5', 999, 1000, 40, '2020-09-04 14:27:48.607413', null, '12'),
       (1, 406, 'item_origin_6', 999, null, null, '2020-09-04 14:27:48.607413', null, '345'),
       (1, 407, 'item_origin_7', 0, null, 40, now(), null, '1'),
       (2, 408, 'item_origin_8', null, null, 40, now(), null, '123'),
       (2, 409, 'item_origin_9', 999, 999, 10, now(), null, null),
       (2, 410, 'item_origin_10', null, null, 40, now(), null, '123');
