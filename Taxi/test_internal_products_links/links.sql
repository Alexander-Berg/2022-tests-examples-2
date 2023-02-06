BEGIN TRANSACTION;

-- Добавляем лавки
INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, title, timezone, region_id, currency, status, source, timetable)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        CURRENT_TIMESTAMP,
        'lavka_1',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
             'foot',
             '{"type": "MultiPolygon", "coordinates": [[[[10.0, 10.0], [20.0, 10.0], [20.0, 20.0], [10.0, 20.0], [10.0, 10.0]]]]}',
             ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
             'active'
                )
            ]::catalog_wms.extended_zone_v1[],
        'Title лавки',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        'WMS'::catalog_wms.depot_source,
        ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[]);


INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '222',
        '2019-12-01 01:01:01.000000+00',
        'lavka_2',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
             'foot',
             '{"type": "MultiPolygon", "coordinates": [[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]]}'::JSONB,
             ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
             'active'
                )
            ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        1,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source);


UPDATE catalog_wms.depots
SET root_category_id = 'ffffffff-ffff-ffff-ffff-ffffffffffff',
    assortment_id = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT',
    price_list_id = 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST';

-- Добавляем категории
INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'active', 'Root_name', 'Root category', 0, null, array[]::text[], array[]::text[]),
('11111111-1111-1111-1111-000000000001', 'active', 'category_name_1', 'y', 97, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}');

INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('11111111-1111-1111-1111-000000000002', 'active', 'category_name_2.0', 'x', 97, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}'),
('11111111-1111-1111-1111-000000000003', 'active', 'category_name_2.1', 'x', 98, '11111111-1111-1111-1111-000000000002', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}'),
('11111111-1111-1111-1111-000000000004', 'active', 'category_name_2.2', 'x', 99, '11111111-1111-1111-1111-000000000003', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}');

-- Добавляем товары
INSERT INTO catalog_wms.goods(product_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'active', 'product_name_1', 'y', 'x', 28, 'г', 250.0000, '{}', '{}', '{}', '{}'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 'active', 'product_name_2', 'y', 'x', 29, 'г', 252.0000, '{}', '{}', '{}', '{}'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 'active', 'product_name_3', 'y', 'x', 29, 'г', 252.0000, '{}', '{}', '{}', '{}'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', 'active', 'product_name_4', 'y', 'x', 29, 'г', 252.0000, '{}', '{}', '{}', '{}');

-- Добавляем товары в категории
INSERT INTO catalog_wms.goods_categories(product_id, category_id)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', '11111111-1111-1111-1111-000000000002'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000004'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000002'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000004');

-- Добавляем категории в лавки
INSERT INTO catalog.eats_categories_mappings
(depot_id, category_id, eats_category_id)
VALUES
(111, '11111111-1111-1111-1111-000000000001', 221),
(111, '11111111-1111-1111-1111-000000000002', 222),
(111, '11111111-1111-1111-1111-000000000003', 223),
(111, '11111111-1111-1111-1111-000000000004', 224),
(222, '11111111-1111-1111-1111-000000000004', 224);

-- Добавляем товары в лавки
INSERT INTO catalog.eats_goods_mappings
(depot_id, product_id, category_id, eats_id)
VALUES
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000', '11111111-1111-1111-1111-000000000001', 330),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000002', 332),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000004', 333),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000004', 334);

COMMIT TRANSACTION ;
