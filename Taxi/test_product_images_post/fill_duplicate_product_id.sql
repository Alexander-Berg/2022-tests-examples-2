insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111112');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from)
values (1, 6, 'item_origin_1', 999, null, null);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 6, 100);
