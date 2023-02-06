-- dictionary
insert into eats_nomenclature.measure_units (id, value,name)
values  (1, 'GRM','г'),
        (2, 'KGRM','кг'),
        (3, 'LT','л'),
        (4, 'MLT','мл');

insert into eats_nomenclature.volume_units (id, value, name)
values  (1, 'CMQ', 'см3'),
        (2, 'DMQ', 'дм3');

-- data
insert into eats_nomenclature.brands (id)
values (1),
       (2);

insert into eats_nomenclature.places (id, slug, is_enabled) 
values (1, 'place_1', true),
       (2, 'place_2', true),
       (3, 'disabled', false),
       (4, 'different_brand', true);

insert into eats_nomenclature.brand_places (brand_id, place_id) 
values (1, 1),
       (1, 2),
       (1, 3),
       (2, 4);

insert into eats_nomenclature.assortments 
values (1),
       (2),
       (3),
       (4);

insert into eats_nomenclature.place_assortments (place_id, assortment_id)
values (1, 1),
       (2, 2),
       (3, 3),
       (4, 4);

insert into eats_nomenclature.sku (id, uuid, alternate_name)
values (1, '11111111-1111-1111-1111-111111111111', 'sku1'),
       (2, '22222222-1111-1111-1111-111111111111', 'sku2'),
       (3, '33333333-1111-1111-1111-111111111111', 'sku3'),
       (4, '00000000-0000-0000-0000-000000000004', 'overriden_sku');

insert into eats_nomenclature.products (id, sku_id, origin_id, name, public_id, quantum, measure_unit_id, measure_value, volume_unit_id, volume_value, brand_id, is_catch_weight)
values (1, null, 'origin_1', 'Place-1_Префикс-1_1', '11111111-1111-1111-1111-111111111111', 0.1, 1, 10, null, null, 1, false),
       (2, 1, 'origin_2', 'Place-1_Префикс-1_2', '22222222-2222-2222-2222-222222222222', 0.1, 2, 10, null, null, 1, false),
       (3, null, 'origin_3', 'Place-1_Префикс-2_1', '33333333-3333-3333-3333-333333333333', 0.1, null, null, null, null, 1, false),
       (4, 2, 'origin_4', 'Place-2_Префикс-1_1', '44444444-4444-4444-4444-444444444444', 0.0, null, null, 1, 10, 1, false),
       (5, null, 'origin_5', 'Place-2_Префикс-2_1', '55555555-5555-5555-5555-555555555555', 0.0, null, null, null, null, 1, false),
       (6, null, 'origin_6', 'Disabled-Place_Префикс-1_1', '66666666-6666-6666-6666-666666666666', 0.0, null, null, null, null, 1, false),
       (7, null, 'origin_7', 'Different-Brand_Префикс-1_1', '77777777-7777-7777-7777-777777777777', 0.0, null, null, null, null, 2, false),
       (8, 1, 'origin_8', 'Place-1_Префикс-1_overriden-sku', '00000000-0000-0000-0000-000000000008', 0.1, 1, 10, null, null, 1, false),
       (9, null, 'origin_9', 'Place-1_Префикс-1_outdated', '00000000-0000-0000-0000-000000000009', 0.1, 1, 10, null, null, 1, false),
       (10, 1, 'origin_10', 'Place-1_Префикс-1_overriden-with-null-sku', '00000000-0000-0000-0000-000000000010', 0.1, 1, 10, null, null, 1, false),
       (11, null, 'origin_11', 'Place-1_Префикс-1_is_catch_weight_true', '00000000-0000-0000-0000-000000000011', 0.4, 3, 20, null, null, 1, true);

alter sequence eats_nomenclature.products_id_seq restart with 50;

insert into eats_nomenclature.overriden_product_sku (product_id, sku_id)
values (8, 4),
       (10, null);

insert into eats_nomenclature.products_usage (product_id, last_referenced_at)
values (1, '2021-09-30T14:00:00'),
       (2, '2021-09-30T14:00:00'),
       (3, '2021-09-30T14:00:00'),
       (4, '2021-09-30T14:00:00'),
       (5, '2021-09-30T14:00:00'),
       (6, '2021-09-30T14:00:00'),
       (7, '2021-09-30T14:00:00'),
       (8, '2021-09-30T14:00:00'),
       (9, '2020-08-30T14:00:00'), -- old timestamp for outdated item;
       (10, '2021-09-30T14:00:00'),
       (11, '2021-09-30T14:00:00');

insert into eats_nomenclature.pictures (id, url, processed_url, hash)
values (1, 'pr_1_null', null, null),
       (2, 'pr_1_not_null', 'processed_url_2', '2'),
       (3, 'pr_2', 'processed_url_3', '3'),
       (4, 'pr_3', 'processed_url_4', '4'),
       (5, 'pr_none', 'processed_url_5', '5');
alter sequence eats_nomenclature.pictures_id_seq restart with 50;       

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (1, 1),
       (1, 2),
       (2, 3),
       (3, 4);

insert into eats_nomenclature.categories (id, assortment_id, name, origin_id)
values
       (1, 1, 'cat_place-1', 'origin_1'),
       (2, 2, 'cat_place-2', 'origin_2'),
       (3, 3, 'cat_place-3', 'origin_3'),
       (4, 4, 'cat_place-4', 'origin_4');
alter sequence eats_nomenclature.categories_id_seq restart with 50;

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 1, 1),
       (1, 1, 2),
       (1, 1, 3),
       (2, 2, 4),
       (2, 2, 5),
       (3, 3, 6),
       (4, 4, 7);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, '11111111-db68-5e4e-a9a4-9ded1bf241e5', 'тип 1'),
       (2, '22222222-db68-5e4e-a9a4-9ded1bf241e5', 'тип 2'),
       (3, '33333333-db68-5e4e-a9a4-9ded1bf241e5', 'тип 3'),
       (4, '00000000-0000-0000-0000-000000000004', 'overriden type');

insert into eats_nomenclature.product_attributes (product_id, product_type_id)
values (1, 1),
       (2, 2),
       (4, 3);

insert into eats_nomenclature.sku_attributes (sku_id, product_type_id)
values (1, 3),
       (2, 2),
       (4, 4);

insert into eats_nomenclature.overriden_product_attributes (product_id, product_type_id)
values (4, 1);
