INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, title, timezone, region_id, currency, status, source)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        CURRENT_TIMESTAMP,
        'test_lavka',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811], [37.387111, 55.835444], [37.386596, 55.839791], [37.383549, 55.842254], [37.377927, 55.845007], [37.361834, 55.852443], [37.346148, 55.860264], [37.341824, 55.85925], [37.341208, 55.852081], [37.337072, 55.845345], [37.347886, 55.843945], [37.347803999999999, 55.84095], [37.350561, 55.839954], [37.351901, 55.837823], [37.350258, 55.835197], [37.349695, 55.834379], [37.347803, 55.832593], [37.355012, 55.831314], [37.356771, 55.831356], [37.359217, 55.832461], [37.36089, 55.834049], [37.361235, 55.836529], [37.357459, 55.838429], [37.351969, 55.84049], [37.354034, 55.841715], [37.357821, 55.839818], [37.362992, 55.838922], [37.371618, 55.840757]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Title лавки',
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS'),
        ('aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
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
('11111111-1111-1111-1111-000000000001', 'active', 'category name 1', 'category desc 1', 1, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"cat_1.jpg"}', array[]::text[])
;

INSERT INTO catalog_wms.goods(product_id, external_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '7771', 'active', 'good name 1', 'good full name 1', 'good name desc 1', 1, 'г', 250.000, '{"url_1.jpg"}', '{}', '{}', '{}'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '7772', 'active', 'good name 2', 'good full name 2', 'good name desc 2', 2, 'г', 100.000, '{"url_2.jpg"}', '{}', '{}', '{}'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '7773', 'active', 'good name 3', 'good full name 3', 'good name desc 3', 2, 'г', 100.000, '{"url_3.jpg"}', '{}', '{}', '{}')
;

UPDATE catalog_wms.goods SET vat = '20.00';

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', '11111111-1111-1111-1111-000000000001')
;

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', product_id
FROM catalog_wms.goods;

INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price, shelf_type)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 1000.0000, 'markdown'::catalog_wms.shelf_type_t),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 1000.0000, 'markdown'::catalog_wms.shelf_type_t),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003', 1000.0000, 'markdown'::catalog_wms.shelf_type_t)
;

CREATE TEMP TABLE stocks (
     product_id TEXT,
     in_stock NUMERIC(19, 4),
     depleted TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP - INTERVAL '1 hour',
     shelf_type catalog_wms.shelf_type_t NOT NULL DEFAULT 'markdown'::catalog_wms.shelf_type_t
);

INSERT INTO stocks(product_id, in_stock)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 123.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000003', 10.0000)
;

INSERT INTO catalog_wms.stocks(depot_id, product_id, in_stock, depleted, shelf_type)
SELECT d.depot_id,
       s.product_id,
       s.in_stock,
       s.depleted,
       s.shelf_type
FROM catalog_wms.depots d,
     stocks s;

DROP TABLE stocks;
