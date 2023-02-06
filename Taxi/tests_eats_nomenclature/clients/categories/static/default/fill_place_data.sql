insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 1
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 2
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = null
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1'), (1, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 2, null, 2), (1, 3, null, null);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3'), ('vendor_4', '');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values (1, '1', '1', 1, 1, '1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       (2, '2', '2', 2, 1, '2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'),
       (3, '3', '3', 2, 2, '3', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'),
       (4, '4', '4', 3, 4, '4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'),
       (5, '5', '5', 3, 3, '5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005'),
       (6, '6', '6', 3, 3, '6', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006'),
       (7, '7', '7', 3, 3, '7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007');

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1'),
       (22, '1_1'),
       (33, '1_1_1'),
       (44, '1_1_2'),
       (55, '1_1_2_3'),
       (66, '1_2'),
       (77, '2'),
       (88, '2_1');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base)
values
       (1, 11, 1, '1', '1_origin', false, false),
       (2, 22, 1, '1_1', '1_1_origin', true, true),
       (3, 33, 1, '1_1_1', '1_1_1_origin', false, false),
       (4, 44, 1, '1_1_2', '1_1_2_origin', false, true),
       (5, 55, 1, '1_1_2_3', '1_1_2_3_origin', false, false),
       (6, 66, 1, '1_2', '1_2_origin', false, false),
       (7, 77, 1, '2', '2_origin', false, false),
       (8, 88, 1, '2_1', '2_1_origin', true, false),
       -- assortment 2
       (9, 11, 2, '1', '1_origin', false, false),
       (10, 22, 2, '1_1', '1_1_origin', true, true),
       (11, 66, 2, '1_2', '1_2_origin', false, false),
       (12, 77, 2, '2', '2_origin', false, false);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3),
       (2, 1, 1, 5),
       (3, 2, 1, 6),
       (4, 2, 1, 9),
       (5, 4, 1, 23),
       (6, 1, 1, 65),
       (7, null, 1, 23),
       (8, 7, 1, 87),
       -- assortment 2
       (9, null, 2, 45),
       (10, 9, 2, 2),
       (11, 9, 2, 87),
       (12, null, 2, 67);

insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', null, null),
       ('url_3', 'processed_url_3', '3'),
       ('url_4', 'processed_url_4', '4'),
       ('url_5', 'processed_url_5', '5');

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 3, 1, 100),
       (1, 3, 2, 50),
       (1, 3, 3, 10),
       (1, 5, 4, 100),
       (1, 5, 5, 20),
       (1, 5, 6, 30),
       (1, 8, 7, 40),
       (1, 8, 1, 40),
       -- assortment 2
       (2, 10, 1, 40),
       (2, 10, 2, 40);

insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 5, 5),
       (2, 9, 5);
