DELETE FROM catalog.eats_goods_mappings WHERE product_id = '6ed08cd0-68f4-11e9-b7fd-ac1f6b8566c7';

INSERT INTO catalog_wms.stocks(depot_id, product_id, in_stock, depleted, shelf_type)
VALUES
('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000', '6ed08cd0-68f4-11e9-b7fd-ac1f6b8566c7', 5.0, CURRENT_TIMESTAMP - INTERVAL '1 hour', 'markdown'::catalog_wms.shelf_type_t),
('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000', '2ede2faf-f4ba-2109-57ef-5c1f6b8569b1', 14.0, CURRENT_TIMESTAMP - INTERVAL '1 hour', 'markdown'::catalog_wms.shelf_type_t);

DELETE FROM catalog_wms.price_list_items WHERE 
price_list_id = 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST' AND
product_id = '6ed08cd0-68f4-11e9-b7fd-ac1f6b8566c7';

DELETE FROM catalog_wms.price_list_items WHERE 
price_list_id = 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST' AND
product_id = '2ede2faf-f4ba-2109-57ef-5c1f6b8569b1';

INSERT INTO catalog_wms.price_list_items(item_id, price_list_id, product_id, price, shelf_type)
VALUES
('6ed08cd0-68f4-11e9-b7fd-ac1f6b8566c7_md_PRICE', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '6ed08cd0-68f4-11e9-b7fd-ac1f6b8566c7', 124.0, 'markdown'::catalog_wms.shelf_type_t),
('2ede2faf-f4ba-2109-57ef-5c1f6b8569b1_md_PRICE', 'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST', '2ede2faf-f4ba-2109-57ef-5c1f6b8569b1', 79.0, 'markdown'::catalog_wms.shelf_type_t);

