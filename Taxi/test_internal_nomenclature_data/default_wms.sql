-- depot_id: 'id-111', region_id: 111
-- depot_id: 'id-222', region_id: 222
INSERT INTO catalog_wms.depots (depot_id, external_id, region_id, updated, name, location, zone, timezone, currency, status, source, timetable)
VALUES
('id-111', '90213', 111, CURRENT_TIMESTAMP, 'lavka_baryshixaaaaaaa', (37.371618, 55.840757)::catalog_wms.depot_location, '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.362992, 55.838922], [37.371618, 55.840757]]]]}', 'Europe/Moscow', 'RUB', 'active'::catalog_wms.depot_status, '1C'::catalog_wms.depot_source, ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[]),
('id-222', '87840', 222, CURRENT_TIMESTAMP, 'lavka_malomoskovskaya', (37.371618, 55.840757)::catalog_wms.depot_location, '{"type": "MultiPolygon", "coordinates": [[[[37.668148, 55.820834], [37.669757, 55.824326], [37.668148, 55.820834]]]]}', 'Europe/Moscow', 'RUB', 'active'::catalog_wms.depot_status, '1C'::catalog_wms.depot_source, ARRAY[('everyday'::catalog_wms.day_type, ('07:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[])
;

UPDATE catalog_wms.depots
SET root_category_id = 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
    assortment_id = '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT',
    price_list_id = 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST';

INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'active', 'Корень 1', 'Корневая категория', 0, null, array[]::text[], array[]::text[]),
('73fa0267-8519-485a-9e06-5e18a9a7514c', 'active', 'Завтрак', 'Завтрак', 173, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', '{}', '{}'),
('61d24b27-0e8e-4173-a861-95c87802972f', 'active', 'Яйца', 'Яйца', 97, '73fa0267-8519-485a-9e06-5e18a9a7514c', '{}', '{}')
;

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.goods(product_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7', 'active', 'Twinings Lady Grey', 'Чай Twinings Lady Grey черный, 25 шт', 'Чай Twinings Lady Grey черный, 25 шт', 0, 'шт', 25.0000, '{}', '{}', '{}', '{}'),
('0326d831-877f-11e9-b7ff-ac1f6b8569b3', 'active', 'Багет', 'Багет, 160 г', 'Багет, 160 г', 109, 'г', 160.0000, '{}', '{}', '{}', '{}')
;

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7', '61d24b27-0e8e-4173-a861-95c87802972f'),
('0326d831-877f-11e9-b7ff-ac1f6b8569b3', '73fa0267-8519-485a-9e06-5e18a9a7514c')
;


INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', product_id
FROM catalog_wms.goods;


-- Price lists
INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price)
VALUES
('941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7PRICE', 'active', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7', 219.0000),
('0326d831-877f-11e9-b7ff-ac1f6b8569b3PRICE', 'active', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '0326d831-877f-11e9-b7ff-ac1f6b8569b3', 59.0000)
;
