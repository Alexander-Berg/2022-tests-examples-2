INSERT INTO eats_ordershistory.orders (
    order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
    place_id, status, delivery_location, total_amount, is_asap,
    cancel_reason, created_at, delivered_at
) VALUES ('order-id-1', 'eda', 1, NULL, NULL, 123, 'delivered', '(1,1)',
          '123.45', True, NULL, '2021-07-20T12:01:00Z', NULL),
         ('order-id-2', 'eda', 2, NULL, NULL, 456, 'cancelled', '(1,1)',
          '123.45', True, NULL, '2021-07-25T12:01:00Z', NULL),
         ('order-id-3', 'eda', 3, NULL, NULL, 123, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-29T12:01:00Z', NULL),
         ('order-id-4', 'eda', 4, NULL, NULL, 456, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-29T12:01:00Z', NULL);
