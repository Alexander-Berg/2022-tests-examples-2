insert into eats_nomenclature.brands (id) values (777);
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

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_6_force_unavailable', 'pqr', 3, 3, 'item_6_force_unavailable', 0.5, 1, 300, true, true, true, 777, '66666666666666666666666666666666'),
       ('item_origin_7_force_unavailable', 'stu', 3, 3, 'item_7_force_unavailable', 0.5, 1, 300, true, true, true, 777, '77777777777777777777777777777777');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from, full_price, old_full_price, force_unavailable_until)
values (1, 1, 'item_origin_6_force_unavailable', 999, 40, '2020-02-04 03:00:00', 999, 999, '2037-01-08 01:00:00'),
       (1, 2, 'item_origin_7_force_unavailable', 999, 40, null, 999, 999, '2037-01-08 02:00:00');

insert into eats_nomenclature.autodisabled_products(place_id, product_id, disabled_count, last_disabled_at, need_recalculation)
values (1, 1, 1, '2020-10-01 01:00:00', false),
       (1, 2, 2, '2020-12-01 02:00:00', false);

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 10),
       (2, 0);

insert into eats_nomenclature.categories (id, assortment_id, name, origin_id)
values (100, 1, 'category_6_force_unavailable', 'category_6_origin_force_unavailable');

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 100, 1, 30),
       (1, 100, 2, 40);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 1, 100, 2);
