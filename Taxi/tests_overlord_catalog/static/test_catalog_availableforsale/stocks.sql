INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, timetable)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '90213',
        '2019-12-26 15:42:05.199281+03',
        'lavka_baryshixa',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811], [37.387111, 55.835444], [37.386596, 55.839791], [37.383549, 55.842254], [37.377927, 55.845007], [37.361834, 55.852443], [37.346148, 55.860264], [37.341824, 55.85925], [37.341208, 55.852081], [37.337072, 55.845345], [37.347886, 55.843945], [37.347803999999999, 55.84095], [37.350561, 55.839954], [37.351901, 55.837823], [37.350258, 55.835197], [37.349695, 55.834379], [37.347803, 55.832593], [37.355012, 55.831314], [37.356771, 55.831356], [37.359217, 55.832461], [37.36089, 55.834049], [37.361235, 55.836529], [37.357459, 55.838429], [37.351969, 55.84049], [37.354034, 55.841715], [37.357821, 55.839818], [37.362992, 55.838922], [37.371618, 55.840757]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[]);

UPDATE catalog_wms.depots
SET root_category_id = 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
    assortment_id = '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT',
    price_list_id = 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST';

INSERT INTO catalog_wms.categories (category_id, parent_id, name, description, legal_restrictions, images, updated) 
VALUES ('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
        NULL,
        'Root',
        'Root',
        '{}',
        '{"(d9ef3613-c0ed-40d2-9fdc-3eed67f55aae,\"\",\"2019-12-26 15:36:36+03\")"}',
        '2019-12-26 15:36:36.727994+03');


INSERT INTO catalog_wms.categories (category_id, parent_id, name, description, legal_restrictions, images, updated) 
VALUES ('7a7d3cd4-4a65-4abc-880d-d1a2f987396d',
        'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
        'Цветы',
        'Цветы',
        '{}',
        '{"(7a7d3cd4-4a65-4abc-880d-d1a2f987396d,\"\",\"2019-12-26 15:36:36+03\")"}',
        '2019-12-26 15:36:36.727994+03');


INSERT INTO catalog_wms.goods (product_id, rank, status, title, long_title, description, legal_restrictions, amount_unit, amount, images, updated, pfc, ingredients)
VALUES ('62a03ba5-c417-11e9-b7ff-ac1f6b8569b3',
        1,
        'active'::catalog_wms.record_status,
        'Букет микс',
        'Букет в плёнке Velvet flowers хризантема одноголовая, роза, альстромерия, 1 шт', 'Букет в плёнке Velvet flowers хризантема одноголовая, роза, альстромерия, 11шт. Производитель: ООО "СНАБСЕРВИС СТОЛИЦА", Россия. Состав: Хризантема одноголовая (1 шт.), Роза одноголовая (3 шт.), Роза кустовая (3 шт.), Альстромерия (4 шт.). Срок хранения, дней: 7.',
        '{}',
        'шт',
        11.0000,
        '{"(62a03ba5-c417-11e9-b7ff-ac1f6b8569b3,https://storage.yandexcloud.net/lavka/i/sku/4680/4680018086737/1.jpg,\"2019-12-26 15:36:36+03\")"}',
        '2019-12-26 15:36:36.727994+03',
        '{}',
        '{}');

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES ('62a03ba5-c417-11e9-b7ff-ac1f6b8569b3', '7a7d3cd4-4a65-4abc-880d-d1a2f987396d');

-- Assortments

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', product_id
FROM catalog_wms.goods;

-- Price lists
INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price)
VALUES
('62a03ba5-c417-11e9-b7ff-ac1f6b8569b3PRICE', 'active', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3', 219.0000);

--Stocks

INSERT INTO catalog_wms.stocks (depot_id, product_id, updated, depleted, in_stock)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3',
        '2019-12-01 01:01:03.000000+00',
        '2019-12-01 01:01:01.000000+00',
        322.0);

-- Non-WMS

DELETE FROM catalog.depot_goods_settings
WHERE depot_id = 90213  
        AND product_id = '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3';

INSERT INTO catalog.depot_goods_settings (depot_id, product_id, sort_order, always_show, price, currency, in_stock_real, updated)
VALUES (90213,
        '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3',
        149,
        true,
        599.0000,
        'RUB',
        322.0,
        '2019-12-01 01:01:02.000000+00');
