insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_8', 'mno', 3, 3, 'item_8', 0.5, 1, 300, true, true, true, 777, '88888888888888888888888888888888');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, vat, available_from, full_price, old_full_price)
values (1, 8, 'item_origin_8', null, null, null, null, null);

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values (2, 'category_6', 'category_6_origin');

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (2, 6, 8, 21);
