-- Brand, place and assortments
insert into eats_nomenclature.brands (id, slug) values (777, 'lavka');
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, '1', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);
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

insert into eats_nomenclature.marking_types(value)
values
    ('default'),
    ('tobacco');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, marking_type_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111111', 1),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 1, 1000, true, true, true, 777, '22222222222222222222222222222222', null),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333333333333333333333333333', null),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 1, 50, true, true, false, 777, '44444444444444444444444444444444', 1),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777, '55555555555555555555555555555555', 2);

insert into eats_nomenclature.products_usage (product_id, last_referenced_at)
values (1, '2021-10-07 10:00:00'),
       (2, '2021-10-07 10:00:00'),
       (3, '2021-10-07 10:00:00'),
       (4, '2021-10-08 14:00:00'),
       (5, '2021-10-07 10:00:00');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from, full_price, old_full_price)
values (1, 1, 'item_origin_1', 999, null, null, 999, null),
       (1, 2, 'item_origin_2', 999, 10, now(), 999, 999),
       (1, 3, 'item_origin_3', 999, 20, '2017-01-08 04:05:06', 999, 999),
       (1, 4, 'item_origin_4', 999, 30, '2037-01-08', 999, 999),
       (1, 5, 'item_origin_5', 999, 40, '2020-09-04 14:27:48.607413', 999, 999);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 10), 
       (2, 20),
       (3, 30),
       (4, 0),
       (5, null);

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
       (1, 'category_1', 'category_1_origin'),
       (1, 'category_2', 'category_2_origin'),
       (1, 'category_3', 'category_3_origin'),
       (1, 'category_4', 'category_4_origin'),
       (1, 'category_5', 'category_5_origin');

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash, needs_subscription)
values ('url_1', 'processed_url_1', '1', true),
       ('url_2', null, null, true),
       ('url_3', 'processed_url_3', '3', false),
       ('url_4', 'processed_url_4', '4', false),
       ('url_5', 'processed_url_5', '5', true);

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX000', 9, 3);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 100),
       (1, 1, 2, 50),
       (1, 3, 3, 10),
       (1, 3, 4, 100),
       (1, 3, 5, 20);

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (1, 1),
       (2, 2);

-- Category Pictures
insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 1, 2),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 5, 5);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (1, 3),
       (2, 1),
       (3, 2),
       (4, 1),
       (5, 3);

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values (1, 1, 100, null),
       (1, 2, 100, null),
       (1, 3, 100, 2),
       (1, 4, 100, null);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 0),
       (1, 1, 2, 0),
       (1, 1, 3, 0),
       (1, 1, 4, 0),
       (1, 1, 5, 0);

insert into eats_nomenclature.retailers (id, name, slug)
values (777, 'slug', 'slug');
