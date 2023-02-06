-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 1
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 2
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = null
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1'), (1, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 2, null, 2), (1, 3, null, null);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3'), ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005'),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'),
       ('item_origin_7', 'pqr', 3, 3, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007');


insert into eats_nomenclature.places_products(id, place_id, product_id, origin_id, price, old_price, vat, available_from)
values (31, 1, 401, 'item_origin_1', 999, null, null, null),
       (32, 1, 402, 'item_origin_2', 999, 999, 10, now()),
       (33, 1, 403, 'item_origin_3', 999, 1000, 20, '2017-01-08 04:05:06'),
       (34, 1, 404, 'item_origin_4', 999, 1000, 30, '2037-01-08'),
       (35, 1, 405, 'item_origin_5', 999, 1000, 40, '2020-09-04 14:27:48.607413'),
       (36, 1, 406, 'item_origin_6', 999, null, null, null),
       (37, 1, 407, 'item_origin_7', 999, null, null, null);
alter sequence eats_nomenclature.places_products_id_seq restart with 50;

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id, is_custom, is_base)
values
       (1, 'base_custom_category_1', 'base_custom_category_1_origin', true, true),
       (1, 'category_2', 'category_2_origin', false, true),
       (1, 'category_3', 'category_3_origin', false, true),
       (1, 'category_4', 'category_4_origin', false, true),
       (1, 'category_5', 'category_5_origin', false, true),
       (1, 'category_6', 'category_6_origin', false, true),
       (1, 'custom_category_1', 'custom_category_1_origin', true, false);

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
       (1, 7, 407, 40),
       (1, 7, 401, 40);

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
       (1, 4, 100, 6),
       (1, 6, 100, null),
       (1, 7, 100, null);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (31, 20),
       (32, 99),
       (33, null);

