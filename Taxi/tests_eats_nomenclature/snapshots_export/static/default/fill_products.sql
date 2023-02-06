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

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.sku(id, uuid, alternate_name)
values (1, '111', '111'),
       (2, '222', '222'),
       (3, '333', '333');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, composition, volume_value, sku_id)
values ( 'item_origin_1', null, 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111-1111-1111-1111-111111111111', null, null, null),
       ( 'item_origin_2', 'def', 2, 1, 'item_2', 1.0, 2, 1000, true, true, true, 777, '22222222-2222-2222-2222-222222222222', 'composition2', null, null),
       ( 'item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333-3333-3333-3333-333333333333', 'composition3', 100, null),
       ( 'item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 3, 50, true, false, false, 777, '44444444-4444-4444-4444-444444444444', 'composition4', null, null),
       ( 'item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 4, 300, true, true, true, 777, '55555555-5555-5555-5555-555555555555', 'composition5', null, null),
       ( 'item_origin_6', 'pqr', 3, 3, 'item_6', 0.3, 1, 300, false, true, true, 778, '66666666-6666-6666-6666-666666666666', 'composition6', null, null),
       ( 'item_origin_7', 'stu', 3, 3, 'item_7', 1.0, 1, 1000, false, false, true, 778, '77777777-7777-7777-7777-777777777777', 'composition7', null, null),
       ( 'item_origin_8', 'vwx', 3, 3, 'item_8', 1.0, 1, 2000, false, false, true, 778, '88888888-8888-8888-8888-888888888888', 'composition8', null, 1),
       ( 'item_origin_9', 'zzz', 3, 3, 'item_9', 1.0, 1, 2000, false, false, true, 778, '99999999-9999-9999-9999-999999999999', 'composition9', null, 2),
       ( 'item_origin_10', 'product_with_overriden_sku', 3, 3, 'item_10', 1.0, 1, 2000, false, false, true, 778, '00000000-0000-0000-0000-000000000010', 'composition10', null, 1),
       ( 'item_origin_11', 'product_with_overriden_null_sku', 3, 3, 'item_10', 1.0, 1, 2000, false, false, true, 778, '00000000-0000-0000-0000-000000000011', 'composition11', null, 1);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from)
values (1, 1, 'item_origin_1', null, null, null, null, null),
       (1, 2, 'item_origin_2', 999, 10, null, null, null),
       (1, 3, 'item_origin_3', 100, 50, 200, 150, '2017-01-08 04:05:06'),
       (2, 4, 'item_origin_4', null, null, null, null, '2017-01-08 04:05:06'),
       (2, 5, 'item_origin_5', 999, 40, 500, 400, '2020-02-04 14:27:48.607413'),
       (3, 6, 'item_origin_6', 999, 40, 500, 400, '2017-01-08 04:05:06'),
       (3, 7, 'item_origin_7', 100, 50, 200, 150, '2018-01-08 04:05:06'),
       (4, 8, 'item_origin_8', 101, 51, 201, 151, '2018-01-08 04:05:06'),
       (4, 10, 'item_origin_10', 101, 51, 201, 151, '2018-01-08 04:05:06'),
       (4, 11, 'item_origin_11', 101, 51, 201, 151, '2018-01-08 04:05:06');

insert into eats_nomenclature.product_brands(value_uuid, value)
values ('product_brand_6_uuid', 'product_brand_6_value'),
       ('product_brand_7_uuid', 'product_brand_7_value'),
       ('product_brand_8_uuid', 'product_brand_8_value'),
       ('product_brand_6_uuid_no_prior', 'product_brand_6_value_no_prior'),
       ('product_brand_9_uuid', 'product_brand_9_value'),
       ('overriden_sku_uuid', 'overriden_sku_value');

insert into eats_nomenclature.product_types(value_uuid, value)
values ('product_type_6_uuid', 'product_type_6_value'),
       ('product_type_7_uuid', 'product_type_7_value'),
       ('product_type_8_uuid', 'product_type_8_value'),
       ('product_type_6_uuid_no_prior', 'product_type_6_value_no_prior'),
       ('product_type_9_uuid', 'product_type_9_value'),
       ('overriden_sku_uuid', 'overriden_sku_value');

insert into eats_nomenclature.overriden_product_attributes(product_id, product_brand_id, product_type_id)
values (6, 1, 1),
       (7, null, null),
       (9, null, 5);

insert into eats_nomenclature.sku_attributes(sku_id, product_brand_id, product_type_id)
values (1, 3, 3),
       (2, null, null),
       (3, 6, 6);

insert into eats_nomenclature.overriden_product_sku(product_id, sku_id)
values (10, 3),
       (11, null);

insert into eats_nomenclature.product_attributes(product_id, product_brand_id, product_type_id)
values (5, null, null),
       (6, 4, 4),
       (7, 2, 2),
       (8, null, null),
       (9, 5, null);
       
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id)
values (1, 222, 1);

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (2, 1);

insert into eats_nomenclature.pictures(url, processed_url)
values ('url1', 'processed_url1');

insert into eats_nomenclature.product_pictures(product_id, picture_id)
values (1, 1);
