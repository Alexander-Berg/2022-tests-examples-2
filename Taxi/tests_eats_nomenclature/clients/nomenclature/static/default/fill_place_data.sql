-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments(id) values (default), (default), (default), (default), (default);
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1'), (1, 'assortment_name_2'), (1, 'experiment_assortment_name');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 3, null, 2), (1, 4, null, null), (1, 5, null, 3);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), 
       ('vendor_2', 'country_2'), 
       ('vendor_3', 'country_3'), 
       ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id,public_id)
values ('item_origin_1_avail_null', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       ('item_origin_2_avail_now', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'),
       ('item_origin_3_avail_past', 'ghi', 2, 2, 'item_3', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'),
       ('item_origin_4_avail_future', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'),
       ('item_origin_5_avail_past_zero_stock', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005'),
       ('item_origin_6_avail_past_null_stock', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'),
       ('item_origin_7_zero_price', 'mno', 3, 3, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007'),
       ('item_origin_8_null_price', 'mno', 3, 3, 'item_8', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008'),
       ('item_origin_9_avail_past_diff_assortment', 'ghi', 2, 2, 'item_9', 0.0, 3, null, true, false, true, 1, '44333333333333333333333333333333'),
       ('item_origin_10_avail_future_diff_assortment', 'jkl', 3, 2, 'item_10', 0.0, null, 40, false, false, true, 1, '55444444444444444444444444444444'),
       ('item_origin_11_zero_old_price', 'def', 2, 1, 'item_11', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b011'),
       ('item_origin_12_force_unavailable', 'mno', 3, 2, 'item_12', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012');


alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from, force_unavailable_until)
values (1, 401, 'item_origin_1_avail_null', 999, null, null, null, null),
       (1, 402, 'item_origin_2_avail_now', 999, 999, 10, now(), null),
       (1, 403, 'item_origin_3_avail_past', 99.9, 1000, 20, '2017-01-08 04:05:06', null),
       (1, 404, 'item_origin_4_avail_future', 999, 1000, 30, '2037-01-08', null),
       (1, 405, 'item_origin_5_avail_past_zero_stock', 999, 1000, 40, '2020-09-04 14:27:48.607413', null),
       (1, 406, 'item_origin_6_avail_past_null_stock', 999, null, null, '2020-09-04 14:27:48.607413', null),
       (1, 407, 'item_origin_7_zero_price', 0, null, 40, now(), null),
       (1, 408, 'item_origin_8_null_price', null, null, 40, now(), null),
       (1, 409, 'item_origin_9_avail_past_diff_assortment', 999, 999, 10, now(), null),
       (1, 410, 'item_origin_10_avail_future_diff_assortment', 99.9, 1000, 20, '2017-01-08 04:05:06', null),
       (1, 411, 'item_origin_11_zero_old_price', 999, 0, 10, now(), null),
       (1, 412, 'item_origin_12_force_unavailable', 999, 1000, 20, '2017-01-08 04:05:06', '2037-01-08 03:00:00');

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
       (1, 'category_1', 'category_1_origin'),
       (1, 'category_2', 'category_2_origin'),
       (1, 'category_3', 'category_3_origin'),
       (1, 'category_4', 'category_4_origin'),
       (1, 'category_5', 'category_5_origin'),
       (1, 'category_6', 'category_6_origin'),
       (2, 'category_7', 'category_7_origin');

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', null, null),
       ('url_3', 'processed_url_3', '3'),
       ('url_4', 'processed_url_4', '4'),
       ('url_5', 'processed_url_5', '5');

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX000', 9, 3);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 401, 100),
       (1, 1, 402, 50),
       (1, 2, 403, 10),
       (1, 3, 404, 100),
       (1, 3, 405, 20),
       (1, 6, 406, 30),
       (1, 6, 407, 20),
       (1, 6, 408, 20),
       (2, 7, 409, 20),
       (2, 7, 410, 20),
       (1, 1, 411, 50),
       (1, 3, 412, 60);

insert into eats_nomenclature.product_pictures (product_id, picture_id, updated_at)
values (401, 1, '2017-01-08 04:05:06+03:00'),
       (402, 2, '2017-01-08 04:05:06+03:00');

-- Category Pictures
insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 5, 5);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (401, 3),
       (402, 1),
       (403, 2),
       (403, 3),
       (404, 1),
       (405, 3),
       (406, 3);

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id, sort_order, parent_category_id)
values (1, 1, 100, 4),
       (1, 2, 100, 1),
       (1, 3, 100, 2),
       (1, 4, 100, null),
       (1, 6, 100, 1);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (31, 20), 
       (32, 99), 
       (33, 40), 
       (34, 20), 
       (35, 0), 
       (37, 2),
       (38, 3),
       (39, 2),
       (40, 3),
       (41, 100),
       (42, 10);
