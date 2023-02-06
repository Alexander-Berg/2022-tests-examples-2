-- Brand, place and assortments
insert into eats_nomenclature.brands (id, slug) 
values (1, 'brand1'), 
       (2, 'brand2'),
       (3, 'brand3');

insert into eats_nomenclature.places (id, slug) 
values (1, '1'), 
       (2, '2'),
       (3, '3'),
       (4, '4'),
       (5, '5');

insert into eats_nomenclature.brand_places (brand_id, place_id) 
values (1, 1), 
       (2, 2),
       (3, 5);

insert into eats_nomenclature.assortments(id) 
values (default), 
       (default), 
       (default), 
       (default), 
       (default),
       (default);

insert into eats_nomenclature.assortment_traits (id, brand_id, assortment_name)
values (1, 1, 'assortment_name_1'), 
       (2, 2, 'assortment_name_2'), 
       (3, 2, 'assortment_name_3');

insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), 
       (1, 2, null, null), -- partners
       (2, 3, null, null), -- partners
       (2, 4, null, 2),
       (2, 5, null, 3),
       (3, 6, null, null); -- partners

--- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'),
       ('vendor_2', 'country_2'),
       ('vendor_3', 'country_3'),
       ('vendor_4', '');

insert into eats_nomenclature.sku (id, uuid, alternate_name)
values (1, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000001', '1'),
       (2, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000002', '2'),
       (3, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000003', '3'),
       (4, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000004', '4'),
       (5, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000005', '5'),
       (6, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000006', '6'),
       (7, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000007', '7'),
       (8, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000008', '8'),
       (9, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000009', '9'),
       (10, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000010', '10'),
       (11, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000011', '11'),
       (12, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000012', '12'),
       (13, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000013', '13'),
       (14, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000014', '14'),
       (15, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000015', '15'),
       (16, 'e2f1aa3c-e1e7-404b-8d0b-7c931e000016', '16');

alter sequence eats_nomenclature.products_id_seq restart with 401;
insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 1),
       ('item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 2),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 3),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 4),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005', 5),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006', 6),
       ('item_origin_7', 'stu', 3, 3, 'item_7', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 7),
       ('item_origin_8', 'stu', 3, 3, 'item_8', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008', 8),
       ('item_origin_9', 'stu', 3, 3, 'item_9', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009', 9),
       ('item_origin_10', 'stu', 3, 3, 'item_10', 0.0, null, null, false, false, true, 3, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010', 10),
       ('item_origin_11', 'stu', 3, 3, 'item_11', 0.0, null, null, false, false, true, 3, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b011', 11),
       ('item_origin_12', 'stu', 3, 3, 'item_12', 0.0, null, null, false, false, true, 3, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012', 12),
       ('item_origin_13', 'stu', 3, 3, 'item_13', 0.0, null, null, false, false, true, 3, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013', 13),
       ('item_origin_14', 'override sku', 3, 3, 'item_14', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b014', 13),
       ('item_origin_15', 'set sku from overriden', 3, 3, 'item_15', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b015', null),
       ('item_origin_16', 'set sku from overriden to null', 3, 3, 'item_16', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b016', 16);

insert into eats_nomenclature.overriden_product_sku(product_id, sku_id)
values (409, 9),
       (414, 14),
       (415, 15),
       (416, null);

alter sequence eats_nomenclature.places_products_id_seq restart with 31;
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, force_unavailable_until)
values -- brand_id: 1
       (1, 401, 'item_origin_1', '2021-09-30T05:00:00'), 
       (1, 402, 'item_origin_2', '2021-09-30T05:00:00'),
       (1, 403, 'item_origin_3', null),
       (1, 404, 'item_origin_4', '2020-01-04T00:00:00'),
       (1, 405, 'item_origin_5', '2020-01-04T00:00:00'),
       (1, 406, 'item_origin_6', '2020-01-04T00:00:00'),
       (1, 414, 'item_origin_14', '2020-01-04T00:00:00'),
       (1, 415, 'item_origin_15', '2020-01-04T00:00:00'),
       (1, 416, 'item_origin_16', '2020-01-01T12:00:00'),
       -- brand_id: 2
       (2, 407, 'item_origin_5', '2020-01-13T12:00:00'),
       (2, 408, 'item_origin_6', '2020-01-01T12:00:00'),
       (2, 409, 'item_origin_7', '2020-01-01T12:00:00'),
       -- brand_id: 3 (without master-tree)
       (5, 413, 'item_origin_13', '2020-01-01T12:00:00');

insert into eats_nomenclature.custom_categories(id, name, external_id)
values (1, 'custom_category_1', 1),
       (2, 'custom_category_2', 2),
       (3, 'custom_category_3', 3),
       (4, 'custom_category_4', 4),
       (5, 'custom_category_5', 5),
       (6, 'custom_category_6', 6),
       (7, 'custom_category_7', 7);

insert into eats_nomenclature.categories(id, assortment_id, custom_category_id, name)
values (1, 1, 1, 'category_1'),
       (2, 1, 2, 'category_2'),
       (3, 2, 3, 'category_3'),
       (4, 2, 4, 'category_4'),
       (5, 2, 5, 'category_5'),
       (6, 3, 6, 'category_6'),
       (7, 5, 7, 'category_7');

insert into eats_nomenclature.categories_products(assortment_id, category_id, product_id)
values -- master tree assortment (brand_id = 1)
       (1, 1, 401),
       (1, 1, 402),
       (1, 2, 403),
       (1, 2, 404),
       (1, 2, 414),
       (1, 2, 415),
       (1, 2, 416),
       -- partners assortment (brand_id = 1)
       (2, 4, 401),
       (2, 4, 402),
       (2, 5, 403),
       (2, 5, 404),
       (2, 3, 405),
       (2, 3, 406),
       -- partners assortment (brand_id = 2)
       (3, 6, 407),
       (3, 6, 408),
       (3, 6, 409),
       -- master tree assortment (brand_id = 2)
       (5, 7, 408),
       (5, 7, 409);

insert into eats_nomenclature.categories_relations(assortment_id, category_id)
values -- brand_id = 1
       (1, 1),
       (1, 2),
       (2, 3),
       (2, 4),
       (2, 5),
       -- brand_id = 2
       (3, 6),
       (5, 7);

insert into eats_nomenclature.custom_categories_groups(id, name)
values (1, '1'),
       (2, '2');

insert into eats_nomenclature.product_types(id, value_uuid, value)
values (1, 'f4be531c-3783-4a28-a13c-279fec780001', 'type_1'),
       (2, 'f4be531c-3783-4a28-a13c-279fec780002', 'type_2'),
       (3, 'f4be531c-3783-4a28-a13c-279fec780003', 'type_3'),
       (4, 'f4be531c-3783-4a28-a13c-279fec780004', 'type_4'),
       (5, 'f4be531c-3783-4a28-a13c-279fec780005', 'type_5'),
       (6, 'f4be531c-3783-4a28-a13c-279fec780006', 'type_6');

insert into eats_nomenclature.custom_categories_product_types(custom_category_id, product_type_id)
values (1, 1),
       (2, 2),
       (3, 3),
       (5, 5);

insert into eats_nomenclature.custom_categories_relations(custom_category_group_id, custom_category_id)
values (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (2, 5);

insert into eats_nomenclature.brands_custom_categories_groups(brand_id, custom_categories_group_id, trait_id)
values (1, 1, 1),
       (2, 2, 3);

insert into eats_nomenclature.product_attributes(product_id, product_type_id)
values (401, 1),
       (404, 1),
       (405, 5),
       (408, 1),
       (409, 1);

insert into eats_nomenclature.sku_attributes(sku_id, product_type_id)
values (2, 2),
       (3, 5),
       (4, 2),
       (14, 2),
       (15, 2);

insert into eats_nomenclature.overriden_product_attributes(product_id, product_type_id)
values (403, 3),
       (404, 4),
       (405, 5),
       (408, 4),
       (409, 4);

insert into eats_nomenclature.products_usage(product_id, last_referenced_at)
values (401, now() - interval '1 days'),
       (402, now() - interval '3 days'),
       (407, now() - interval '1 days');
