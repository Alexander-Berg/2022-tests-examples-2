-- depot_id: 'id-111', region_id: 1
INSERT INTO catalog_wms.depots (depot_id, external_id, region_id, updated, name, location, zone, timezone, currency, status, source, timetable)
VALUES
('id-111', '90213', 1, CURRENT_TIMESTAMP, 'lavka_1', (37.371618, 55.840757)::catalog_wms.depot_location, '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.362992, 55.838922], [37.371618, 55.840757]]]]}', 'Europe/Moscow', 'RUB', 'active'::catalog_wms.depot_status, '1C'::catalog_wms.depot_source, ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[])
;

UPDATE catalog_wms.depots
SET root_category_id = 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
    assortment_id = '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT',
    price_list_id = 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST';

INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions, deep_link)
VALUES
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'active', 'Корень 1', 'Корневая категория', 0, null, array[]::text[], array[]::text[], 'test_deep_link'),
('543af1b2-f97d-4d37-8039-a5f6b3dcd26d', 'active', 'Йогурт питьевой', 'Йогурт питьевой', 173, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', '{}', '{}', 'test_deep_link')
;

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.goods(product_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('836d5980-689f-11e9-b7fd-ac1f6b8566c7', 'active', 'Actimel 2,5% клубника', 'Функциональный напиток Actimel клубника в упаковке, 100 г', 'Actimel функциональный напиток клубника в упаковке, 100г. Производитель: Данон Индустрия ООО, Россия. Срок хранения: 35 дней. Условия хранения: при +4(±2)°C. Белки: 2,65г. Жиры: 2,5г. Углеводы: 11,5г. Калорийность: 79ккал.', 0, 'г', 100.0, '{"https://images.testsuite/134336879/{w}x{h}.jpeg"}', '{}', '{}', '{}')
;

UPDATE catalog_wms.goods SET vat = '20.00';

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('836d5980-689f-11e9-b7fd-ac1f6b8566c7', '543af1b2-f97d-4d37-8039-a5f6b3dcd26d')
;


INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', product_id
FROM catalog_wms.goods;


-- Price lists
INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price)
VALUES
('941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7PRICE', 'active', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '836d5980-689f-11e9-b7fd-ac1f6b8566c7', 34.0000)
;

CREATE TEMP TABLE stocks (
    product_id TEXT,
    in_stock NUMERIC(19, 4)
);

INSERT INTO stocks(product_id, in_stock)
VALUES
('836d5980-689f-11e9-b7fd-ac1f6b8566c7', 27.0000);

-- Now populate stocks for depots
INSERT INTO catalog_wms.stocks(depot_id, product_id, in_stock)
SELECT d.depot_id,
       s.product_id,
       s.in_stock
FROM catalog_wms.depots d,
     stocks s;

DROP TABLE stocks;
