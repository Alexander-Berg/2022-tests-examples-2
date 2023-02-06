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
values (1, '00000000-0000-0000-0000-000000000000', 'sku_match'),
       (2, '00000000-0000-0000-0000-000000000001', 'sku_match_different'),
       (3, '00000000-0000-0000-0000-000000000002', 'sku_mismatch');

insert into eats_nomenclature.products (id, sku_id, origin_id, name, public_id, quantum, measure_unit_id, measure_value, volume_unit_id, volume_value, brand_id, is_catch_weight)
values (1, null, 'origin_1', 'product_type_match', '00000000-0000-0000-0000-000000000001', 0.1, 1, 10, null, null, 1, false),
       (2, null, 'origin_2', 'product_type_match_same', '00000000-0000-0000-0000-000000000002', 0.1, 1, 10, null, null, 1, false),
       (3, null, 'origin_3', 'product_type_match_different', '00000000-0000-0000-0000-000000000003', 0.1, 1, 10, null, null, 1, false),
       (4, null, 'origin_4', 'overriden_product_type_match', '00000000-0000-0000-0000-000000000004', 0.1, 1, 10, null, null, 1, false),
       (5, 1, 'origin_5', 'sku_type_match', '00000000-0000-0000-0000-000000000005', 0.1, 1, 10, null, null, 1, false),
       (6, 3, 'origin_6', 'overriden_sku_type_match', '00000000-0000-0000-0000-000000000006', 0.1, 1, 10, null, null, 1, false),
       (7, null, 'origin_7', 'null_product_type', '00000000-0000-0000-0000-000000000007', 0.1, 1, 10, null, null, 1, false),
       (8, null, 'origin_8', 'different_brand', '00000000-0000-0000-0000-000000000008', 0.1, 1, 10, null, null, 2, false),
       (9, null, 'origin_9', 'outdated', '00000000-0000-0000-0000-000000000009', 0.1, 1, 10, null, null, 1, false),
       (10, 1, 'origin_10', 'overriden_with_null_sku', '00000000-0000-0000-0000-000000000010', 0.1, 1, 10, null, null, 1, false),
       (11, 1, 'origin_11', 'overriden_sku_mismatch', '00000000-0000-0000-0000-000000000011', 0.1, 1, 10, null, null, 1, false),
       (12, 1, 'origin_12', 'overriden_sku_match_different', '00000000-0000-0000-0000-000000000012', 0.1, 1, 10, null, null, 1, false),
       (13, 1, 'origin_13', 'overriden_attributes_mismatch', '00000000-0000-0000-0000-000000000013', 0.1, 1, 10, null, null, 1, false),
       (14, null, 'origin_14', 'match_after_page_with_mismatch', '00000000-0000-0000-0000-000000000014', 0.1, 1, 10, null, null, 1, false),
       (15, null, 'origin_15', 'is_catch_weight_true', '00000000-0000-0000-0000-000000000015', 0.4, 3, 20, null, null, 1, true);

alter sequence eats_nomenclature.products_id_seq restart with 50;

insert into eats_nomenclature.products_usage (product_id, last_referenced_at)
values (1, '2021-09-30T14:00:00'),
       (2, '2021-09-30T14:00:00'),
       (3, '2021-09-30T14:00:00'),
       (4, '2021-09-30T14:00:00'),
       (5, '2021-09-30T14:00:00'),
       (6, '2021-09-30T14:00:00'),
       (7, '2021-09-30T14:00:00'),
       (8, '2021-09-30T14:00:00'),
       (9, '2020-09-30T14:00:00'), -- old timestamp for outdated item
       (10, '2021-09-30T14:00:00'),
       (11, '2021-09-30T14:00:00'),
       (12, '2021-09-30T14:00:00'),
       (13, '2021-09-30T14:00:00'),
       (14, '2021-09-30T14:00:00'),
       (15, '2021-09-30T14:00:00');

insert into eats_nomenclature.overriden_product_sku (product_id, sku_id)
values (6, 1),
       (10, null),
       (11, 3),
       (12, 2);

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
       (1, 1, 4),
       (1, 1, 5),
       (1, 1, 6),
       (1, 1, 7),
       (4, 4, 8), -- different brand
       (1, 1, 9),
       (1, 1, 10),
       (1, 1, 11),
       (1, 1, 12),
       (1, 1, 13),
       (1, 1, 14),
       (1, 1, 15);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, '00000000-0000-0000-0000-000000000001', 'Тип товара'),
       (2, '00000000-0000-0000-0000-000000000002', 'Другой тип товара'),
       (3, '00000000-0000-0000-0000-000000000003', 'Пип товара');

insert into eats_nomenclature.product_attributes (product_id, product_type_id)
values (1, 1),
       (2, 1),
       (3, 2),
       (4, 3),
       (7, null),
       (13, 1);

insert into eats_nomenclature.sku_attributes (sku_id, product_type_id)
values (1, 1),
       (2, 2),
       (3, 3);

insert into eats_nomenclature.overriden_product_attributes (product_id, product_type_id)
values (4, 1),
       (13, 3),
       (14, 1),
       (15, 1);
