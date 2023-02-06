-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (777), (778);
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true),
       (2, '2', true),
       (3, '3', false),
       (4, '4', true),
       (5, '5', true);
insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 1),
       (777, 2),
       (778, 3),
       (778, 4),
       (778, 5);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- inactive for place 1
insert into eats_nomenclature.assortments default values; -- active for place 1 with trait_id = 1
insert into eats_nomenclature.assortments default values; -- active for place 4
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1'),
       (778, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, 2, null), 
       (1, 3, null, 1),
       (4, 4, null, null),
       (5, null, null, null);
insert into eats_nomenclature.assortment_enrichment_statuses(assortment_id, are_custom_categories_ready, enrichment_started_at)
values (2, true, '2017-01-05 00:05:00');

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, composition)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111-1111-1111-1111-111111111111', 'composition1'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 2, 1000, true, true, true, 777, '22222222-2222-2222-2222-222222222222', 'composition2'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333-3333-3333-3333-333333333333', null),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 3, 50, true, false, false, 777, '44444444-4444-4444-4444-444444444444', null),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 4, 300, true, true, true, 777, '55555555-5555-5555-5555-555555555555', null),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.3, 1, 300, false, true, true, 778, '66666666-6666-6666-6666-666666666666', null),
       ('item_origin_7', 'stu', 3, 3, 'item_7', 1.0, 1, 1000, false, false, true, 778, '77777777-7777-7777-7777-777777777777', null),
       ('item_origin_8', 'vwx', 3, 3, 'item_8', 1.0, 1, 2000, false, false, true, 778, '88888888-8888-8888-8888-888888888888', null),
       ('item_with_no_category', 'azaza', 3, 3, 'item_9', 1.0, 1, 2000, false, false, true, 778, '99999999-9999-9999-9999-999999999999', null),
       ('item_for_stock_limit_test', 'ololo', 3, 3, 'item_9', 1.0, 1, 2000, false, false, true, 778, '00000000-0000-0000-0000-000000000010', null);

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, full_price, old_full_price, available_from)
values (1, 1, 'item_origin_1', null, null, null, null, null, null),
       (1, 2, 'item_origin_2', 999.45, 10.10, 10, null, null, null),
       (1, 3, 'item_origin_3', 100, 50, -10, 200, 150, '2017-01-08 04:05:06'),
       (2, 4, 'item_origin_4', null, null, null, null, null, '2017-01-08 04:05:06'),
       (2, 5, 'item_origin_5', 999, 40, null, 500, 400, '2020-02-04 14:27:48.607413'),
       (3, 6, 'item_origin_6', 999, 40, null, 500, 400, '2017-01-08 04:05:06'),
       (3, 7, 'item_origin_7', 100, 50, null, 200, 150, '2018-01-08 04:05:06'),
       (4, 8, 'item_origin_8', 101, 51, 20, 201, 151, '2018-01-08 04:05:06'),
       (3, 9, 'item_with_no_category', 101, 51, null, 201, 151, '2018-01-08 04:05:06'),
       (1, 10, 'item_for_stock_limit_test', 101, 51, null, 201, 151, '2018-01-08 04:05:06');

-- Categories
insert into eats_nomenclature.categories_dictionary (id, name)
values
       (1, 'category_1'),
       (2, 'category_2'),
       (3, 'category_3'),
       (4, 'category_4'),
       (5, 'category_5'),
       (6, 'category_6'),
       (7, 'category_7'),
       (8, 'category_8'),
       (9, 'category_9');

insert into eats_nomenclature.categories (assortment_id, name, public_id, is_base)
values
       (1, 'category_1', 1, true),
       (1, 'category_2', 2, true),
       (1, 'category_3', 3, true),
       (1, 'category_4', 4, false),
       (3, 'category_5', 5, true),
       (3, 'category_6', 6, true),
       (3, 'category_7', 7, false),
       (1, 'category_8', 8, false),
       (3, 'category_2', 2, true),
       (3, 'category_3', 3, true),
       (3, 'category_4', 4, true),
       (4, 'category_5', 5, false);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 1, 1),
       (1, 1, 2),
       (1, 4, 2),
       (1, 4, 3),
       (1, 8, 1),
       (1, 8, 2),
       (1, 1, 10),
       (3, 6, 1),
       (3, 6, 2),
       (3, 7, 3),
       (3, 11, 2),
       (3, 11, 3),
       (4, 12, 8);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 0), 
       (2, 20),
       (3, null),
       (4, 40),
       (5, null),
       (6, 1000),
       (7, 0),
       (8, 10),
       (9, 100),
       (10, 3);
