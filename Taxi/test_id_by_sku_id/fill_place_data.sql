-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1), (2);
insert into eats_nomenclature.places (id, slug) values (1, 'slug'), (2, 'slug2'), (3, 'slug3');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (2, 2), (1, 3);
insert into eats_nomenclature.assortments(id)
values (1), (2), (3), (4),
       (5), (6), (7), (8),
       (9), (10), (11), (12);
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'exp_assortment_name'), (1, 'assortment_name'), (1, 'default_assortment_name'), (1, 'some_assortment');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, trait_id)
values (1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, null),
       (2, 5, 1), (2, 6, 2), (2, 7, 3), (2, 8, null),
       (3, 9, 1), (3, 10, 2), (3, 11, 3), (3, 12, null), (3, null, 4);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 3), (2, 3), (3, 3);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), 
       ('vendor_2', 'country_2'), 
       ('vendor_3', 'country_3'), 
       ('vendor_4', '');

alter sequence eats_nomenclature.sku_id_seq restart with 120;
insert into eats_nomenclature.sku (id, uuid, alternate_name)
values (120, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120', '1'),
       (121, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', '2'),
       (122, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122', '3'),
       (123, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', '4'),
       (124, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124', '5'),
       (125, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'should not be visible'),
       (126, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126', 'overriden sku'),
       (127, '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127', 'reused sku');

alter sequence eats_nomenclature.products_id_seq restart with 401;
insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (401, 'item_origin_1', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 120),
       (402, 'item_origin_2', 'def', 2, 1, 'item_2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 121),
       (403, 'item_origin_3', 'ghi', 2, 2, 'item_3', 0.5, null, null, false, true, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 122),
       (404, 'item_origin_1', 'jkl', 3, 4, 'item_4', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 120),
       (405, 'item_origin_2', 'mno', 3, 3, 'item_5', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005', 121),
       (406, 'item_origin_4', 'pqr', 3, 3, 'item_6', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006', 123),
       (407, 'item_origin_5', 'mno', 3, 3, 'item_7', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', null),
       (408, 'item_origin_6', 'mno', 3, 3, 'item_8', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008', 124),
       (409, 'item_origin_6', 'mno', 3, 3, 'item_8', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009', 124),
       (410, 'overriden_sku', 'mno', 3, 3, 'item', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010', 125),
       (411, 'overriden_with_null_sku', 'mno', 3, 3, 'item', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b011', 125),
       (412, 'same_sku', 'mno', 3, 3, 'item', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012', 127),
       (413, 'same_sku_2', 'mno', 3, 3, 'item', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013', 127);

insert into eats_nomenclature.overriden_product_sku (product_id, sku_id)
values (410, 126),
       (411, null);

-- Category
insert into eats_nomenclature.categories_dictionary(id, name)
values (1, 'category_1'),
       (2, 'category_2'),
       (3, 'category_3'),
       (4, 'category_4'),
       (5, 'category_5');

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id)
values (1, 'category_1', 'category_1_origin', 1),
       (2, 'category_2', 'category_2_origin', 2),
       (3, 'category_3', 'category_3_origin', 3),
       (4, 'category_4', 'category_4_origin', 4),
       (5, 'category_1', 'category_1_origin', 1),
       (6, 'category_2', 'category_2_origin', 2),
       (7, 'category_3', 'category_3_origin', 3),
       (8, 'category_4', 'category_4_origin', 4),
       (9, 'category_1', 'category_1_origin', 1),
       (10, 'category_2', 'category_2_origin', 2),
       (11, 'category_3', 'category_3_origin', 3),
       (12, 'category_4', 'category_4_origin', 4);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
-- первый товар (sku_id = 120)
values (9, 9, 401), -- товар есть в этом магазине во всех ассортиментах
       (10, 10, 401),
       (11, 11, 401),
       (12, 12, 401),
       (1, 1, 401), -- также он есть и в другом магазине бренда
       (2, 2, 401),
       (3, 3, 401),
       (4, 4, 401),
       (5, 5, 404), -- также он есть в другом бренде под той же мастер-карточкой
       (6, 6, 404),
       (7, 7, 404),
       (8, 8, 404),
-- второй товар (sku_id = 121)
       (3, 3, 402), -- товар есть только в другом магазине
       (7, 7, 405), -- и в другом бренде под той же мастер-карточкой
-- третий товар (sku_id = 122)
       (9, 9, 403), -- товар есть только в этом магазине
       (10, 10, 403),
       (11, 11, 403),
       (12, 12, 403),
-- четвертый товар (sku_id = 123)
       (5, 5, 406), -- товар есть только в другом бренде
-- пятый товар (sku_id is null)
       (9, 9, 407), -- товар без мастер-карточки
-- шестой товар (sku_id = 124)
       (9, 9, 408), -- товар есть в этом магазине только в одном ассортименте
       (1, 1, 408), -- также он есть и в другом магазине бренда во всех ассориментах
       (2, 2, 408),
       (3, 3, 408),
       (4, 4, 408),
       (5, 5, 409), -- также он есть в другом бренде под той же мастер-карточкой
       (6, 6, 409),
       (7, 7, 409),
       (8, 8, 409),
-- товар с перегруженным sku
       (9, 9, 410), -- товар есть в этом магазине во всех ассортиментах
       (10, 10, 410),
       (11, 11, 410),
       (12, 12, 410),
-- товар с перегруженным null sku
       (9, 9, 411), -- товар есть в этом магазине во всех ассортиментах
       (10, 10, 411),
       (11, 11, 411),
       (12, 12, 411),
-- товары с одинаковым sku
       (9, 9, 412), -- товар есть в этом магазине во всех ассортиментах
       (10, 10, 412),
       (11, 11, 412),
       (12, 12, 412),
       (9, 9, 413), -- товар есть в этом магазине во всех ассортиментах
       (10, 10, 413),
       (11, 11, 413),
       (12, 12, 413);

