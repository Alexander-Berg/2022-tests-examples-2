-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true),
       (2, '2', false),
       (3, '3', true),
       (4, '4', true),
       (5, '5', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111111'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 1, 1000, true, true, true, 777, '22222222222222222222222222222222'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333333333333333333333333333'),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 1, 50, true, true, false, 777, '44444444444444444444444444444444'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777, '55555555555555555555555555555555');

-- item_6 - new product, item_7 - old product
insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, created_at)
values ('item_origin_6', 'pqr', 1, 1, 'item_6', 0.2, 1, 1000, false, false, true, 777, '66666666666666666666666666666666', now() - interval '13 hours'),
       ('item_origin_7', 'stu', 1, 1, 'item_7', 0.2, 1, 1000, false, false, true, 777, '77777777777777777777777777777777', now() - interval '15 hours');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(id, place_id, product_id, origin_id, price, vat, available_from)
values (1, 1, 1, 'item_origin_1', 999, null, null),
       (2, 1, 2, 'item_origin_2', 998, 10, now()),
       (3, 1, 3, 'item_origin_3', 997, 20, '2017-01-08 04:05:06'),
       (4, 1, 4, 'item_origin_4', 996, 30, '2037-01-08'),
       (5, 1, 5, 'item_origin_5', 999, 40, '2020-09-04 14:27:48.607413'),
       (6, 1, 7, 'item_origin_7', 999, 10, now());

insert into eats_nomenclature.stocks (place_product_id, value)
values (6, 0.00);

-- Picture
insert into eats_nomenclature.pictures (id, url, processed_url, hash)
values (1, 'url_1', 'processed_url_1', '1'),
       (2, 'url_2', null, null),
       (3, 'url_3', 'processed_url_3', '3'),
       (4, 'url_4', 'processed_url_4', '4'),
       (5, 'url_5', 'processed_url_5', '5');

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX000', 9, 3);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (1, 3),
       (2, 1),
       (3, 2),
       (4, 1),
       (5, 3),
       (7, 1);

insert into eats_nomenclature.product_brands(value_uuid, value)
values ('39181c7c-5c13-5512-bd2c-20c11d7b4984', 'brand1');

insert into eats_nomenclature.product_types(value_uuid, value)
values ('484a55c8-dc57-5b52-83c3-b23ffa24f97e', 'type1');

-- Product Attributes
insert into eats_nomenclature.product_attributes(product_id, product_brand_id, product_type_id)
values (7, 1, 1);

insert into eats_nomenclature.custom_categories(name, picture_id, description, external_id)
values ('custom category 1', 1, 'abc', 1);

-- Product Custom Categories
insert into eats_nomenclature.custom_categories_products(custom_category_id, product_id)
values (1, 7);

insert into eats_nomenclature.assortments(id, created_at)
values (1, now()),
       (2, now() - interval '10 hours'),
       (3, now() - interval '11 hours'),
       (4, now() - interval '12 hours'),
       (5, now() - interval '13 hours'),
       (6, now() - interval '14 hours'),
       (7, now() - interval '15 hours'),
       (8, now() - interval '16 hours'),
       (9, now() - interval '17 hours');

insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, updated_at)
values (1, 1, null, now()),
       (2, 1, 2, now() - interval '10 hours'),
       (3, 3, 2, now() - interval '11 hours'),
       (4, null, 2, now() - interval '12 hours'),
       (5, 1, null, now() - interval '13 hours');

insert into eats_nomenclature.categories (id, assortment_id, name, origin_id, updated_at)
values (1, 1, 'data1', 'done1', now()),
       (2, 2, 'data2', 'done2', now() - interval '10 hours'),
       (3, 3, 'data3', 'done3', now() - interval '11 hours'),
       (4, 4, 'data4', 'done4', now() - interval '12 hours'),
       (5, 4, 'data5', 'done5', now() - interval '13 hours');

insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values (1, 1, 100, null),
       (2, 2, 100, null),
       (3, 3, 100, null),
       (4, 4, 100, null),
       (4, 5, 100, 4);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 100),
       (1, 1, 2, 50),
       (2, 2, 3, 10),
       (2, 2, 4, 10),
       (2, 2, 5, 10),
       (3, 3, 1, 100),
       (4, 4, 3, 100),
       (4, 5, 4, 100);

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (1, 1),
       (2, 2),
       (7, 1);

insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id, updated_at)
values (1, 1, 1, now()),
       (2, 2, 2, now() - interval '10 hours'),
       (3, 3, 3, now() - interval '11 hours'),
       (4, 4, 4, now() - interval '12 hours'),
       (4, 5, 5, now() - interval '13 hours');

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count, updated_at)
values (1, 1, 1, 100, now()),
       (2, 2, 2, 200, now() - interval '10 hours'),
       (3, 3, 3, 300, now() - interval '11 hours'),
       (4, 4, 4, 400, now() - interval '12 hours'),
       (4, 5, 5, 500, now() - interval '13 hours');

insert into eats_nomenclature.assortment_enrichment_statuses (assortment_id, are_custom_categories_ready, enrichment_started_at, updated_at)
values (1, true, now(), now()),
       (2, true, now() - interval '10 hours', now() - interval '10 hours'),
       (3, false, now() - interval '11 hours', now()),
       (4, false, now() - interval '12 hours', now() - interval '12 hours'),
       (5, true, now() - interval '13 hours', now() - interval '13 hours');

insert into eats_nomenclature.upload_tasks(id, assortment_id, data, status, details, updated_at)
values (1, 1, 'data1', 'done', 'details1', now()),
       (2, 2, 'data2', 'done', 'details2', now() - interval '10 hours'),
       (3, 3, 'data3', 'done', 'details3', now() - interval '11 hours'),
       (4, 4, 'data4', 'done', 'details4', now() - interval '12 hours'),
       (5, 5, 'data5', 'done', 'details5', now() - interval '13 hours'),
       (6, 6, 'data6', 'error', 'details6', now() - interval '10 hours');

insert into eats_nomenclature.upload_task_status_history(upload_task_id, status, details, set_at)
values (1, 'done', 'details12', now()),
       (1, 'done', 'details1', now() - interval '10 hours'),
       (2, 'done', 'details2', now() - interval '11 hours'),
       (3, 'done', 'details2', now() - interval '12 hours'),
       (4, 'done', 'details2', now() - interval '13 hours'),
       (5, 'done', 'details2', now() - interval '14 hours'),
       (6, 'error', 'details2', now() - interval '10 hours');

insert into eats_nomenclature.upload_stock_tasks(id, assortment_id, data, status, details, updated_at)
values (1, 1, 'data1', 'done', 'details1', now()),
       (2, 2, 'data2', 'done', 'details2', now() - interval '10 hours'),
       (3, 3, 'data3', 'done', 'details3', now() - interval '11 hours'),
       (4, 4, 'data4', 'done', 'details4', now() - interval '12 hours'),
       (5, 5, 'data5', 'done', 'details5', now() - interval '13 hours'),
       (6, 7, 'data6', 'canceled', 'details6', now() - interval '10 hours');

insert into eats_nomenclature.upload_stock_task_status_history(upload_task_id, status, details, set_at)
values (1, 'done', 'details12', now()),
       (1, 'done', 'details1', now() - interval '10 hours'),
       (2, 'done', 'details2', now() - interval '11 hours'),
       (3, 'done', 'details2', now() - interval '12 hours'),
       (4, 'done', 'details2', now() - interval '13 hours'),
       (5, 'done', 'details2', now() - interval '14 hours'),
       (6, 'canceled', 'details2', now() - interval '10 hours');

insert into eats_nomenclature.upload_availability_tasks(id, assortment_id, data, status, details, updated_at, created_at)
values (1, 1, 'data1', 'done', 'details1', now(), now()),
       (2, 2, 'data2', 'done', 'details2', now() - interval '10 hours', now()),
       (3, 3, 'data3', 'done', 'details3', now() - interval '11 hours', now()),
       (4, 4, 'data4', 'done', 'details4', now() - interval '12 hours', now()),
       (5, 5, 'data5', 'done', 'details5', now() - interval '13 hours', now()),
       (6, 8, 'data6', 'error', 'details6', now() - interval '10 hours', now()),
       (7, 9, 'data7', 'error', 'details7', now() - interval '11 hours', now());

insert into eats_nomenclature.upload_availability_task_status_history(upload_task_id, status, details, set_at)
values (1, 'done', 'details12', now()),
       (1, 'done', 'details1', now() - interval '10 hours'),
       (2, 'done', 'details2', now() - interval '11 hours'),
       (3, 'done', 'details2', now() - interval '12 hours'),
       (4, 'done', 'details2', now() - interval '13 hours'),
       (5, 'done', 'details2', now() - interval '14 hours'),
       (6, 'error', 'details2', now() - interval '10 hours'),
       (7, 'error', 'details2', now() - interval '11 hours');
