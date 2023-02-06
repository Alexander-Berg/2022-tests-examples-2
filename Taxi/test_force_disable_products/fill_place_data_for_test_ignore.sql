-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, '1'), (2, '2');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (1, 2);
--- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       ('item_origin_2', 'def', 1, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002');

alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, force_unavailable_until)
values (1, 401, 'item_origin_1', null),
       (2, 402, 'item_origin_2', null);
