INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'active', 'Root_name', 'Root category', 0, null, array[]::text[], array[]::text[]),
('11111111-1111-1111-1111-000000000001', 'active', 'category_name_1', 'y', 97, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}');

INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('11111111-1111-1111-1111-000000000002', 'active', 'category_name_2.0', 'x', 97, 'ffffffff-ffff-ffff-ffff-ffffffffffff', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}'),
('11111111-1111-1111-1111-000000000003', 'active', 'category_name_2.1', 'x', 98, '11111111-1111-1111-1111-000000000002', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}'),
('11111111-1111-1111-1111-000000000004', 'active', 'category_name_2.2', 'x', 99, '11111111-1111-1111-1111-000000000003', '{"(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg,\"2019-12-26 15:36:36+03\")"}', '{}');

INSERT INTO catalog_wms.goods(product_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients, vat)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'active', 'product_name_1', 'y', 'x', 28, 'г', 250.0000, '{}', '{}', '{}', '{}', '20.00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 'active', 'product_name_2', 'y', 'x', 29, 'г', 252.0000, '{}', '{}', '{}', '{}', '20.00'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 'active', 'product_name_3', 'y', 'x', 29, 'г', 252.0000, '{}', '{}', '{}', '{}', '20.00');

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', '11111111-1111-1111-1111-000000000001'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000004'),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000002');

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeeASTMNT', product_id
FROM catalog_wms.goods;

INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 1000.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 1000.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002PRICE', 'active', 'dddddddd-dddd-dddd-dddd-ddddddddddddPRLIST', 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 1000.0000);


CREATE TEMP TABLE stocks (
    product_id TEXT,
    in_stock NUMERIC(19, 4)
);

INSERT INTO stocks(product_id, in_stock)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000001', 10.0000),
('aaaaaaaa-aaaa-aaaa-aaaa-000000000002', 10.0000);

-- Now populate stocks for depots
INSERT INTO catalog_wms.stocks(depot_id, product_id, in_stock)
SELECT 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
       s.product_id,
       s.in_stock
FROM stocks s;

DROP TABLE stocks;


INSERT INTO catalog.eats_categories_mappings
(depot_id, category_id, eats_category_id)
VALUES
(111, '11111111-1111-1111-1111-000000000001', 221),
(111, '11111111-1111-1111-1111-000000000002', 222),
(111, '11111111-1111-1111-1111-000000000003', 223),
(111, '11111111-1111-1111-1111-000000000004', 224);


INSERT INTO catalog.eats_goods_mappings
(depot_id, product_id, category_id, eats_id)
VALUES
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000', '11111111-1111-1111-1111-000000000001', 330),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002', '11111111-1111-1111-1111-000000000002', 332),
(111, 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001', '11111111-1111-1111-1111-000000000004', 333);
