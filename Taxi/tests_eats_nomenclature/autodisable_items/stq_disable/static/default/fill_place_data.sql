-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1), (2);
insert into eats_nomenclature.places (id, slug) values (1, '1'), (2, '2');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (2, 2);
insert into eats_nomenclature.assortments(id) values (default), (default), (default), (default), (default);
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1'), (1, 'assortment_name_2'), (1, 'experiment_assortment_name');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 3, null, 2), (1, 4, null, null), (1, 5, null, 3);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

--- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'),
       ('vendor_2', 'country_2'),
       ('vendor_3', 'country_3'),
       ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005'),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'),
       ('item_origin_7', 'stu', 3, 3, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007');

alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, force_unavailable_until)
values (1, 401, 'item_origin_1', '2021-09-30T05:00:00'),
       (1, 402, 'item_origin_2', '2021-09-30T05:00:00'),
       (1, 403, 'item_origin_3', null),
       (1, 404, 'item_origin_4', '2020-01-04T00:00:00'),
       (1, 405, 'item_origin_5', '2020-01-13T12:00:00'),
       (2, 406, 'item_origin_6', '2020-01-01T12:00:00'),
       (1, 407, 'item_origin_7', '2020-01-01T12:00:00');
