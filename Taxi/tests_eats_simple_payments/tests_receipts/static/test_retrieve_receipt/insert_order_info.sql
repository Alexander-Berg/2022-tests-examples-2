INSERT INTO eats_simple_payments.orders (order_id,
                                 service,
                                 currency)
VALUES ('test_order','eats', 'RUB'),  ('test_order_cashback','eats', 'RUB');

INSERT INTO eats_simple_payments.items_info
(item_id, order_id, place_id, balance_client_id, type)
VALUES ('salad', 'test_order_cashback','1','2','product'),
       ('salad-1', 'test_order_cashback','1','2','product'),
       ('pizza_1', 'test_order_cashback','1','2','product'),
       ('test-1', 'test_order','1','2','product'),
       ('test-2', 'test_order','1','2','product'),
       ('pizza_1', 'test_order','1','2','product'),
       ('service-fee', 'test_order','1','2','service_fee'),
       ('size_1', 'test_order_cashback','1','2','product'),
       ('retail-product', 'test_order','1','2','product'),
    ('retail-product', 'test_order_cashback','1','2','product');
