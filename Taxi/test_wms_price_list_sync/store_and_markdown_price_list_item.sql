INSERT INTO catalog.price_lists(price_list_id, status, title)
VALUES('price_list_id', 'active', 'MSK_MAIN');

INSERT INTO catalog.price_list_items(item_id,status,price_list_id,product_id,price,shelf_type)
VALUES
('item_id_1', 'active', 'price_list_id', 'product_id', 89.0000, 'store'),
('item_id_1', 'active', 'price_list_id', 'product_id', 59.0000, 'markdown');
