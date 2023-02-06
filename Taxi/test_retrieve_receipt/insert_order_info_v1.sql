INSERT INTO eats_payments.orders (order_id,
                                 service,
                                 currency,
                                 api_version)
VALUES ('test_order','eats', 'RUB', 1),  ('test_order_cashback','eats', 'RUB', 1);

INSERT INTO eats_payments.items_info
(item_id, order_id, place_id, balance_client_id, type)
VALUES ('salad', 'test_order_cashback','1','2','product'),
       ('salad-1', 'test_order_cashback','1','2','product'),
       ('pizza_1', 'test_order_cashback','1','2','product'),
       ('size_1', 'test_order_cashback','1','2','product'),
       ('retail-product', 'test_order_cashback','1','2','product');



