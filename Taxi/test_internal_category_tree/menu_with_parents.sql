INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, title, timezone, region_id, currency, status, source)
VALUES  ('aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '222',
        CURRENT_TIMESTAMP,
        'test_lavka_2',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Title лавки 2',
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS');

UPDATE catalog_wms.depots
SET root_category_id = 'ffffffff-ffff-ffff-ffff-ffffffffffff',
    assortment_id = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT',
    price_list_id = 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST';

INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'active', 'root 1', 'wms root category', 0, null, array[]::text[], array[]::text[]),
('11111111-1111-1111-1111-000000000001', 'active', 'category name 1', 'category desc 1', 1, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"cat_1.jpg"}', array[]::text[]),
('11111111-1111-1111-1111-000000000002', 'active', 'category name 2', 'category desc 2', 1, '11111111-1111-1111-1111-000000000001', '{"cat_2.jpg"}', array[]::text[])
;

INSERT INTO catalog_wms.goods(product_id, external_id, status, title, long_title, description, rank, ranks, amount_unit, amount, images, legal_restrictions, pfc, ingredients, parent_id, grades)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '7771', 'active', 'good name 1', 'good full name 1', 'good name desc 1', 1, '{1}', 'г', 250.000, '{"url_1.jpg"}', '{}', '{}', '{}', null, (ARRAY['netto'], null, null)::catalog_wms.product_grades),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '7772', 'active', 'good name 2', 'good full name 2', 'good name desc 2', 2, '{2}', 'г', 100.000, '{"url_2.jpg"}', '{}', '{}', '{}', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', null),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '7773', 'active', 'good name 3', 'good full name 3', 'good name desc 3', 2, '{2}', 'г', 100.000, '{"url_3.jpg"}', '{}', '{}', '{}', null, '({}, null, 123)'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000004', '7774', 'active', 'good name 4', 'good full name 4', 'good name desc 4', 3, '{3}', 'г', 250.000, '{"url_1.jpg"}', '{}', '{}', '{}', null, (ARRAY['netto'], null, null)::catalog_wms.product_grades),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000005', '7775', 'active', 'good name 5', 'good full name 5', 'good name desc 5', 4, '{4}', 'г', 100.000, '{"url_2.jpg"}', '{}', '{}', '{}', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000004', '({}, null, 456)'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000006', '7776', 'active', 'good name 6', 'good full name 6', 'good name desc 6', 4, '{4}', 'г', 100.000, '{"url_3.jpg"}', '{}', '{}', '{}', null, null)
;

UPDATE catalog_wms.goods SET vat = '20.00';

INSERT INTO catalog.depot_category_settings
(depot_id, category_id, sort_order, always_show, updated)
VALUES
(111, '11111111-1111-1111-1111-000000000001', 0, true, CURRENT_TIMESTAMP),
(111, '11111111-1111-1111-1111-000000000002', 0, true, CURRENT_TIMESTAMP)
;

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000002'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000004', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000005', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000006', '11111111-1111-1111-1111-000000000002')
;

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', product_id
FROM catalog_wms.goods;

INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price, updated)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 1000.0000, '2021-08-04T02:39:00+00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 1000.0000, '2021-07-30T18:39:00+00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003', 1000.0000, '2020-12-08T13:10:00+00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000005PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005', 1000.0000, '2021-08-04T12:45:00+00:00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000006PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000006', 0.0000, '2021-01-01T00:00:00+00:00')
;

CREATE TEMP TABLE stocks (
     product_id TEXT,
     in_stock NUMERIC(19, 4),
     depleted TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP - INTERVAL '1 hour'
);

INSERT INTO stocks(product_id, in_stock)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 123.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000004', 0.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000005', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000006', 0.0000)
;

-- Now populate stocks for depots
INSERT INTO catalog_wms.stocks(depot_id, product_id, in_stock, depleted)
SELECT d.depot_id,
       s.product_id,
       s.in_stock,
       s.depleted
FROM catalog_wms.depots d,
     stocks s;

DROP TABLE stocks;


INSERT INTO catalog.eats_categories_mappings
(depot_id, category_id, eats_category_id)
VALUES
(111, '11111111-1111-1111-1111-000000000001', 222),
(111, '11111111-1111-1111-1111-000000000002', 223),
(222, '11111111-1111-1111-1111-000000000001', 224),
(222, '11111111-1111-1111-1111-000000000002', 225);


INSERT INTO catalog.eats_goods_mappings
(depot_id, product_id, category_id, eats_id)
VALUES
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000001', 331),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000001', 332),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000002', 333),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000001', 334),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000001', 335),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000002', 336),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000004', '11111111-1111-1111-1111-000000000001', 337),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005', '11111111-1111-1111-1111-000000000001', 338),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000006', '11111111-1111-1111-1111-000000000002', 339),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000004', '11111111-1111-1111-1111-000000000001', 340),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005', '11111111-1111-1111-1111-000000000001', 341),
(222, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000006', '11111111-1111-1111-1111-000000000002', 342)
;
