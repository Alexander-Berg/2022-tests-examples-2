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
       ('item_origin_10', 'abc', 1, 1, 'item_10', 1.0, 1, 100, 1, 10, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010', null);

insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('1111', '111111111', 1, 1),
       ('2222', '1111111111', 4, 2),
       ('3333', '1111111', 9, 3),
       ('4444', '111111001', 9, 3),
       ('5555', '222222', 9, 3),
       ('6666', '3333330', 9, 3),
       ('7777', '111111111', 9, 3);

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (401, 1),
       (402, 2),
       (403, 3),
       (403, 4),
       (404, 1),
       (405, 5),
       (406, 6),
       (409, 1),
       (410, 7);
