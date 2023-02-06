insert into eats_nomenclature.brands (id) values (555);

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_8_force_unavailable', 'stu', 3, 3, 'item_8_force_unavailable', 0.5, 1, 300, true, true, true, 555, '88888888888888888888888888888888'),
       ('item_origin_8_force_unavailable', 'stu', 3, 3, 'item_8_force_unavailable', 0.5, 1, 300, true, true, true, 777, '88888888888888888888888888888889');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from, full_price, old_full_price, force_unavailable_until)
values (1, 3, 'item_origin_8_force_unavailable', 999, 40, null, 999, 999, '2037-01-08 02:00:00'),  -- old product_id from previous brand
       (1, 4, 'item_origin_8_force_unavailable', 999, 40, null, 999, 999, '2037-01-08 02:00:00');

insert into eats_nomenclature.autodisabled_products(place_id, product_id, disabled_count, last_disabled_at, need_recalculation)
values (1, 3, 2, '2020-12-01 02:00:00', false),
       (1, 4, 2, '2020-12-01 02:00:00', false);

insert into eats_nomenclature.stocks (place_product_id, value)
values (3, 0),
       (4, 0);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 100, 4, 30);
