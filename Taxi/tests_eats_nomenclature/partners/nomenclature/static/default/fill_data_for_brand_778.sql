insert into eats_nomenclature.brands (id) values (778);
insert into eats_nomenclature.places (id, slug, is_enabled) values (2, '2', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (778, 2);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id) values (778, 2, 40, 50, 60);
insert into eats_nomenclature.assortments default values; -- active for place 2
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (2, 4, null, null);

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_8_additional', 'desc', 3, 3, 'item_8_additional', 0.5, 1, 300, true, true, true, 778, '00000000000000000000000000000008');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat)
values (2, 8, 'item_origin_8_additional', 999, 40, 500, 400, '2020-02-04 14:27:48.607413', 0);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (8, null);
