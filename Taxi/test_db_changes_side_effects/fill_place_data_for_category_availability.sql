insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, '1', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- inactive for place 1
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, 2);
insert into eats_nomenclature.assortment_enrichment_statuses(assortment_id, are_custom_categories_ready, enrichment_started_at)
values (2, true, '2017-01-05 00:05:00');

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 1, 1000, true, true, true, 777),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 1, 50, true, true, false, 777),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777),
       ('item_origin_6', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price)
values (1, 1, 'item_origin_1', 999),
       (1, 2, 'item_origin_2', 999),
       (1, 3, 'item_origin_3', 999),
       (1, 4, 'item_origin_4', 999),
       (1, 5, 'item_origin_5', 999),
       (1, 6, 'item_origin_6', 999);

insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
(1, 'category_1', 'category_1_origin'),
(1, 'category_2', 'category_2_origin'),
(1, 'category_3', 'category_3_origin'),
(1, 'category_4', 'category_4_origin'),
(1, 'category_5', 'category_5_origin');

insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values (1, 1, 100, null),
       (1, 2, 100, null),
       (1, 3, 100, 1);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 100),
       (1, 1, 2, 50),
       (1, 1, 3, 10),
       (1, 2, 4, 100),
       (1, 2, 5, 20),
       (1, 3, 6, 20);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 0),
       (1, 1, 2, 0),
       (1, 1, 3, 0);
