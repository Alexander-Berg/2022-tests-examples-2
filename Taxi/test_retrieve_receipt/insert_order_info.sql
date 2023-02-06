INSERT INTO eats_payments.orders (order_id,
                                 service,
                                 currency,
                                 api_version)
VALUES ('test_order','eats', 'RUB', 2),  ('test_order_cashback','eats', 'RUB', 2);

INSERT INTO eats_payments.item_payment_type_revision
(item_id, order_id, payment_type, plus_amount, customer_service_type, revision_id)
VALUES('salad', 'test_order_cashback', 'trust', 799.000000, 'composition_products', '100500'),
      ('salad-1', 'test_order_cashback', 'trust', 0.000000, 'composition_products', '100500'),
      ('salad', 'test_order_cashback', 'trust', 799.000000, 'composition_products', '13022-1234'),
      ('salad-1', 'test_order_cashback', 'trust', 0.000000, 'composition_products', '13022-1234'),
      ('pizza_1', 'test_order_cashback', 'trust', 200.000000, 'composition_products', '13022'),
      ('size_1', 'test_order_cashback', 'trust', 60.000000, 'composition_products', '13022'),
      ('pizza_1', 'test_order_cashback', 'trust', 100.000000, 'composition_products', '13022-1234'),
      ('size_1', 'test_order_cashback', 'trust', 30.000000, 'composition_products', '13022-1234'),
      ('salad-1', 'test_order_cashback', 'trust', 0.000000, 'composition_products', '260931814'),
      ('retail-product', 'test_order_cashback', 'trust', 966.000000, 'composition_products', '260931814');
