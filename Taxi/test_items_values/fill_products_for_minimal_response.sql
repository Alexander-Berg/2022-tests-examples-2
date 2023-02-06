insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values (1, '1', null, 1, 1, '1', 0.1, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat, force_unavailable_until)
values (1, 1, '1', 999, null, null, null, '2017-01-08 04:05:06', 10, null); 

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 10);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 1);
