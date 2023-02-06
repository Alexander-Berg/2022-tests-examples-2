insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_6_force_unavailable', 'pqr', 3, 3, 'item_6_force_unavailable', 0.5, 1, 300, true, true, true, 777, '66666666666666666666666666666666'),
       ('item_origin_7_force_unavailable', 'stu', 3, 3, 'item_7_force_unavailable', 0.5, 1, 300, true, true, true, 777, '77777777777777777777777777777777');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from, full_price, old_full_price, force_unavailable_until)
values (1, 6, 'item_origin_6_force_unavailable', 999, 40, '2020-02-04 03:00:00', 999, 999, '2037-01-08 01:00:00'),
       (1, 7, 'item_origin_7_force_unavailable', 999, 40, null, 999, 999, '2037-01-08 02:00:00');

insert into eats_nomenclature.autodisabled_products(place_id, product_id, disabled_count, last_disabled_at, need_recalculation)
values (1, 6, 1, '2020-10-01 01:00:00', false),
       (1, 7, 2, '2020-12-01 02:00:00', false);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (6, 10),
       (7, 0);

insert into eats_nomenclature.categories (id, assortment_id, name, origin_id)
values (100, 1, 'category_6_force_unavailable', 'category_6_origin_force_unavailable');

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 100, 6, 30),
       (1, 100, 7, 40);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 1, 100, 2);
