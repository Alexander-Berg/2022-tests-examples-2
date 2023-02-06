insert into eats_nomenclature.brands (id) 
values (777),
       (778);
insert into eats_nomenclature.places (id, slug, is_enabled) 
values (1, '1', true),
       (2, '2', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) 
values (777, 1),
       (778, 2);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id) 
values (777, 1, 10, 20, 30),
       (778, 2, 40, 50, 60);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.place_assortments (place_id, assortment_id)
values (1, 1),
       (2, 2);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111111'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 1, 1000, true, true, true, 777, '22222222222222222222222222222222'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333333333333333333333333333'),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 1, 50, true, false, false, 777, '44444444444444444444444444444444'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777, '55555555555555555555555555555555'),
       ('item_origin_6', 'desc', 2, 2, 'item_6', 1.0, null, null, false, true, true, 778, '00000000000000000000000000000006');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat)
values (1, 1, 'item_origin_1', null, null, null, null, null, null),
       (1, 2, 'item_origin_2', 999, 10, null, null, null, 10),
       (1, 3, 'item_origin_3', 100, 50, 200, 150, '2017-01-08 04:05:06', 0),
       (1, 4, 'item_origin_4', null, null, null, null, '2017-01-08 04:05:06', 15),
       (1, 5, 'item_origin_5', 999, 40, 500, 400, '2020-02-04 14:27:48.607413', 0),
       (2, 6, 'item_origin_6', 100, 50, 200, 150, '2017-01-08 04:05:06', 0);

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 0), 
       (2, 20),
       (3, 0),
       (4, 40),
       (5, null),
       (6, 0);
