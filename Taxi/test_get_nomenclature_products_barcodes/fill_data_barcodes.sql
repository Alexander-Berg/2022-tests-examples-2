insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_9', 'abc', 1, 1, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013'),
       ('item_origin_10', 'def', 2, 1, 'item_8', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b014'),
       ('item_origin_11', 'ghi', 2, 2, 'item_9', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b115'),
       ('item_origin_12', 'jkl', 3, 2, 'item_10', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b016');

insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('234ETR45611', '234ETR456', 5, 1),
       ('777UUU42', '777UUU', null, 2),
       ('ZZZ00093', 'ZZZ000', 8, null),
       ('888UUU42', '888UUU', null, null);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 413, 'item_origin_11', 999, null, null, null),
       (1, 414, 'item_origin_12', 999, 999, 10, now()),
       (1, 415, 'item_origin_13', 999, 1000, 20, '2017-01-08 04:05:06'),
       (1, 416, 'item_origin_14', 999, 1000, 30, '2037-01-08');

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 413, 100),
       (1, 1, 414, 50),
       (1, 1, 415, 10),
       (1, 1, 416, 100);

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (413, 4),
       (414, 5),
       (415, 6),
       (416, 7);
