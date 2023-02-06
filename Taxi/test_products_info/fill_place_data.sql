-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments(id) values (default), (default), (default), (default);
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'exp_assortment_name'), (1, 'assortment_name'), (1, 'default_assortment_name');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, trait_id)
values (1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, null);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 3);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), 
       ('vendor_2', 'country_2'), 
       ('vendor_3', 'country_3'), 
       ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       ('item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 0.5, null, null, false, true, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005'),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'),
       ('item_origin_7', 'mno', 3, 3, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007'),
       ('item_origin_8', 'mno', 3, 3, 'item_8', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008'),
       ('item_origin_9_force_unavailable', 'mno', 3, 3, 'item_9', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009');


alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from, full_price, old_full_price, force_unavailable_until)
values (1, 401, 'item_origin_1', 999, null, null, null, 100, 99, null),
       (1, 402, 'item_origin_2', 999, 999, 10, now(), null, null, null),
       (1, 403, 'item_origin_3', 99.9, 1000, 20, '2017-01-08 04:05:06', 100, 101, null),
       (1, 404, 'item_origin_4', 999, 1000, 30, '2037-01-08', null, null, null),
       (1, 405, 'item_origin_5', 999, 1000, 40, '2020-09-04 14:27:48.607413', null, null, null),
       (1, 406, 'item_origin_6', 999, null, null, '2020-09-04 14:27:48.607413', null, null, null),
       (1, 407, 'item_origin_7', 100, null, 40, now(), null, null, null),
       (1, 408, 'item_origin_8', 200, 199, 40, now(), null, null, null),
       (1, 409, 'item_origin_9_force_unavailable', 200, 199, 40, '2017-01-08 04:05:06', null, null, '2037-01-08 03:00:00');

-- Category
insert into eats_nomenclature.categories_dictionary(id, name)
values (1, 'category_1'),
       (2, 'category_2'),
       (3, 'category_3'),
       (4, 'category_4'),
       (5, 'category_5');

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id)
values
       (1, 'category_1', 'category_1_origin', 1),
       (2, 'category_2', 'category_2_origin', 2),
       (3, 'category_3', 'category_3_origin', 3),
       (4, 'category_4', 'category_4_origin', 4),
       (4, 'category_5', 'category_5_origin', 5);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 1, 401),
       (1, 1, 402),
       (1, 1, 403),
       (2, 2, 404),
       (2, 2, 405),
       (2, 2, 406),
       (3, 3, 407),
       (3, 3, 408),
       (4, 4, 401),
       (4, 4, 404),
       (4, 5, 407),
       (4, 5, 408),
       (4, 5, 409);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (31, 20),
       (32, 0),
       (33, 40),
       (34, 20),
       (35, 0);
