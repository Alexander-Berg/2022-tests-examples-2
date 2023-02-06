-- depot_id: 'id-111', region_id: 111
-- depot_id: 'id-222', region_id: 222
INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aa1', 'active', 'Корень 1', 'Корневая категория 1', 0, null, array[]::text[], array[]::text[]),
('73fa0267-8519-485a-9e06-5e18a9a7514c', 'active', 'Завтрак - 1', 'Завтрак 1', 173, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aa1', '{}', '{}'),
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aa2', 'active', 'Корень 2', 'Корневая категория 2', 0, null, array[]::text[], array[]::text[]),
('73fa0267-8519-485a-9e06-5e18a9a7514b', 'active', 'Завтрак - 2', 'Завтрак 2', 173, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aa2', '{}', '{}')
;

INSERT INTO catalog_wms.assortments(assortment_id, status, title, parent_id)
VALUES('63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', 'active', 'Ассортимент 1', null);

INSERT INTO catalog_wms.goods(product_id, status, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('0326d831-877f-11e9-b7ff-ac1f6b8569b3', 'active', 'Багет', 'Багет, 160 г', 'Багет, 160 г', 109, 'г', 160.0000, '{}', '{}', '{}', '{}')
;

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('0326d831-877f-11e9-b7ff-ac1f6b8569b3', '73fa0267-8519-485a-9e06-5e18a9a7514c'),
('0326d831-877f-11e9-b7ff-ac1f6b8569b3', '73fa0267-8519-485a-9e06-5e18a9a7514b')
;


INSERT INTO catalog_wms.assortment_items(item_id, status, assortment_id, product_id)
SELECT product_id || 'AITEM', 'active', '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT', product_id
FROM catalog_wms.goods;


-- Price lists
INSERT INTO catalog_wms.price_lists(price_list_id, status, title)
VALUES ('a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', 'active', 'Прайс-лист 1');

INSERT INTO catalog_wms.price_list_items(item_id, status, price_list_id, product_id, price)
VALUES
('0326d831-877f-11e9-b7ff-ac1f6b8569b3PRICE', 'active', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '0326d831-877f-11e9-b7ff-ac1f6b8569b3', 59.0000)
;
