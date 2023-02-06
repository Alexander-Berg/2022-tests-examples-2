-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug'), (2, 'slug2');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (1, 2);
insert into eats_nomenclature.assortments default values; -- inactive for place 1
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- active for place 2
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (1, 'assortment_name_1'),
       (1, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 2, null, 2), (2, 3, null, null);
insert into eats_nomenclature.nomenclature_files(place_id, file_path, file_datetime, updated_at)
values (1, '/some/path/brand_nomenclature.json', now(), now());

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1),
       ('item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 0.0, null, null, false, false, true, 1),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 0.0, null, null, false, false, true, 1),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 1);

alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 401, 'item_origin_1', 999, null, null, null),
       (1, 402, 'item_origin_2', 999, 999, 10, now()),
       (1, 403, 'item_origin_3', 999, 1000, 20, '2017-01-08 04:05:06'),
       (1, 404, 'item_origin_4', 999, 1000, 30, '2037-01-08'),
       (1, 405, 'item_origin_5', 999, 1000, 40, '2020-09-04 14:27:48.607413'),
       (1, 406, 'item_origin_6', 999, null, null, null);

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
       (1, 'category_1', 'category_1_origin'),
       (1, 'category_2', 'category_2_origin'),
       (1, 'category_3', 'category_3_origin'),
       (1, 'category_4', 'category_4_origin'),
       (1, 'category_5', 'category_5_origin'),
       (1, 'category_6', 'category_6_origin'),
       (2, 'category_1', 'category_1_origin'),
       (2, 'category_2', 'category_2_origin'),
       (2, 'category_3', 'category_3_origin'),
       (2, 'category_7', 'category_7_origin'),
       (2, 'category_8', 'category_8_origin'),
       (2, 'category_9', 'category_9_origin');

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', null, null),
       ('url_3', 'processed_url_3', '3'),
       ('url_4', 'processed_url_4', '4'),
       ('url_5', 'processed_url_5', '5');

-- Modifier group
-- uq: name+min_selected+max_selected+is_required+sort_order+origin_id
insert into eats_nomenclature.modifier_groups(unique_key, name, min_selected, max_selected, is_required, sort_order, origin_id)
values ('modifier_group_101true99modifier_group_1_origin', 'modifier_group_1', 0, 1, true, 99, 'modifier_group_1_origin'),
       ('modifier_group_201true100modifier_group_2_origin', 'modifier_group_2', 0, 1, true, 100, 'modifier_group_2_origin'),
       ('modifier_group_313false50modifier_group_3_origin', 'modifier_group_3', 1, 3, false, 50, 'modifier_group_3_origin');

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
       (2, 7, 401, 100),
       (2, 7, 402, 50),
       (2, 7, 403, 50),
       (2, 9, 404, 200),
       (2, 12, 401, 300);

insert into eats_nomenclature.product_pictures (product_id, picture_id, updated_at)
values (401, 1, '2017-01-08 04:05:06+03:00'),
       (402, 2, '2017-01-08 04:05:06+03:00');

-- Category Pictures
insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 5, 5),
       (2, 7, 1),
       (2, 8, 2),
       (2, 11, 3);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (401, 3),
       (402, 1),
       (403, 2),
       (404, 1),
       (405, 3),
       (406, 3);

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id, sort_order, parent_category_id)
values (1, 1, 100, 4),
       (1, 2, 100, 1),
       (1, 3, 100, 2),
       (1, 4, 100, null),
       (1, 6, 100, 1),
       (2, 10, 100, null),
       (2, 9, 100, 10),
       (2, 11, 100, 10),
       (2, 12, 100, 11),
       (2, 7, 100, 11),
       (2, 8, 100, 11);

-- Places categories
insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values
       (1, 1, 1, 100),
       (1, 1, 2, 200),
       (1, 1, 3, 300),
       (1, 1, 4, 400),
       (1, 1, 5, 500),
       (1, 1, 6, 2),
       (2, 1, 10, 10),
       (2, 1, 9, 20),
       (2, 1, 11, 30),
       (2, 1, 12, 40),
       (2, 1, 7, 50),
       (2, 1, 8, 60);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (31, 20),
       (32, 99),
       (33, null);
