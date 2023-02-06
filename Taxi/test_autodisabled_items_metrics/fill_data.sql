-- Brand, place and assortments
insert into eats_nomenclature.brands (id, slug) values (777, 'brand777'), (888, 'brand888');
insert into eats_nomenclature.places (id, slug, is_enabled)
values  (1, '1', true),
        (2, '2', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values  (777, 1),
                                                                        (888, 2);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, created_at)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 777, '11111111111111111111111111111111', now()),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 1, 1000, true, true, true, 777, '22222222222222222222222222222222', now()),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, null, null, false, true, true, 777, '33333333333333333333333333333333', now()),
       ('item_origin_4', 'jkl', 3, 2, 'item_4', 1.0, 1, 50, true, true, false, 777, '44444444444444444444444444444444', now()),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 777, '55555555555555555555555555555555', now()),
       ('item_origin_6', 'pqr', 1, 1, 'item_6', 0.2, 1, 1000, false, false, true, 777, '66666666666666666666666666666666', now() - interval '13 hours'),
       ('item_origin_7', 'stu', 1, 1, 'item_7', 0.2, 1, 1000, false, false, true, 777, '77777777777777777777777777777777', now() - interval '15 hours');

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(id, place_id, product_id, origin_id, price, vat, available_from, force_unavailable_until)
values (1, 1, 1, 'item_origin_1', 999, null, null, null),
       (2, 1, 2, 'item_origin_2', 998, 10, now(), null),
       (3, 1, 3, 'item_origin_3', 997, 20, '2017-01-08 04:05:06', null),
       (4, 1, 4, 'item_origin_4', 996, 30, '2037-01-08', now() + interval '2 hours'),
       (5, 2, 5, 'item_origin_5', 999, 40, '2020-09-04 14:27:48.607413', now() + interval '2 hours'),
       (6, 2, 7, 'item_origin_7', 999, 10, now(), now() + interval '2 hours');

insert into eats_nomenclature.autodisabled_products (place_id, product_id)
values (1, 4),
       (2, 5),
       (2, 7);
