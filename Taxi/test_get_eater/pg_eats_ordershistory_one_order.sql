INSERT INTO eats_ordershistory.orders (
    order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
    place_id, status, delivery_location, total_amount, is_asap,
    cancel_reason, created_at, delivered_at
) VALUES ('order-id-1', 'eda', 1, NULL, 2, 123, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-20T12:01:00Z', NULL);
