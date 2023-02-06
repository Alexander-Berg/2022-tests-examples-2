-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (777), (778);
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true),
       (2, '2', true),
       (3, '3', false),
       (4, '4', true);
insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 1),
       (777, 2),
       (778, 3),
       (778, 4);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id)
values (777, 1, 10, 20, 30),
       (777, 2, 10, 50, 60),
       (778, 3, 70, 80, 90);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- inactive for place 1
insert into eats_nomenclature.assortments default values; -- active for place 1 with trait_id = 1
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, 2, null), (1, 3, null, 1);
insert into eats_nomenclature.assortment_enrichment_statuses(assortment_id, are_custom_categories_ready, enrichment_started_at)
values (2, true, '2017-01-05 00:05:00');

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, composition)
values ('item_origin_1', 'abc', 1, 1, 'Товар 1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111111', 'composition1'),
       ('item_origin_2', 'def', 2, 1, 'Товар 2', 1.0, 2, 1000, true, true, true, 777, '22222222222222222222222222222222', 'composition2'),
       ('item_origin_3', 'ghi', 2, 2, 'Товар 3', 1.0, null, null, false, true, true, 777, '33333333333333333333333333333333', null),
       ('item_origin_4', 'jkl', 3, 2, 'Товар 4', 1.0, 3, 50, true, false, false, 777, '44444444444444444444444444444444', null),
       ('item_origin_5', 'mno', 3, 3, 'Товар 5', 0.5, 4, 300, true, true, true, 777, '55555555555555555555555555555555', null),
       ('item_origin_6', 'pqr', 3, 3, 'Товар 6', 0.7, 4, 2000, false, true, true, 778, '66666666666666666666666666666666', null),
       ('item_origin_7', 'stu', 3, 3, 'Товар 7', 1.0, 1, 1000, false, false, true, 778, '77777777777777777777777777777777', null),
       ('item_origin_8', 'vwx', 3, 3, 'Товар 8', 1.0, 1, 2600, false, false, true, 778, '88888888888888888888888888888888', null),
       ('item_with_no_category', 'azaza', 3, 3, 'Товар 9', 1.0, 1, 2000, false, false, true, 778, '99999999999999999999999999999999', null),
       ('item_for_stock_limit_test', 'azaza', 3, 3, 'item_10', 1.0, 1, 2000, false, false, true, 778, '00000000000000000000000000000010', null);

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat)
values (1, 1, 'item_origin_1', null, null, null, null, null, null),
       (1, 2, 'item_origin_2', 999, 10, null, null, null, 10),
       (1, 3, 'item_origin_3', 100, 50, 200, 150, '2017-01-08 04:05:06', 12),
       (2, 4, 'item_origin_4', null, null, null, null, '2017-01-08 04:05:06', null),
       (2, 5, 'item_origin_5', 999, 40, 500, 400, '2020-02-04 14:27:48.607413', null),
       (3, 6, 'item_origin_6', 999, 40, 500, 400, '2017-01-08 04:05:06', null),
       (3, 7, 'item_origin_7', 100, 50, 200, 150, '2018-01-08 04:05:06', null),
       (4, 8, 'item_origin_8', 101, 51, 201, 151, '2018-01-08 04:05:06', null),
       (3, 9, 'item_with_no_category', 101, 51, 201, 151, '2018-01-08 04:05:06', null),
       (1, 10, 'item_for_stock_limit_test', 101, 51, 201, 151, '2018-01-08 04:05:06', null);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 0), 
       (2, 20),
       (3, 0),
       (4, 40),
       (5, null),
       (6, 1000),
       (7, 0),
       (8, 10),
       (9, 100),
       (10, 3);

insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', 'processed_url_2', '2'),
       ('url_3', 'processed_url_3', '3');

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (1, 1), (1, 2), (2, 3), (2, 1), (3, 2);

insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX00', 9, 3); -- слишком короткий баркод, не попадет в выгрузку

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (3, 1),
       (3, 2),
       (4, 3);
