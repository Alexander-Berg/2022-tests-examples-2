INSERT INTO cargo_orders.orders
(order_id, waybill_ref, provider_order_id, provider_user_id, updated)
VALUES
('9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'waybill-ref', 'taxi-order', 'taxi_user_id_1', '2020-02-03 16:33:54.827958+03');

INSERT INTO cargo_orders.performer_order_cancel
(id, cargo_order_id, taxi_order_id, park_id, driver_id, cargo_cancel_reason, taxi_cancel_reason, created_ts, completed, guilty, need_reorder, payload, updated_ts)
VALUES
(3, '9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'taxi-order', 'park', 'driver', 'cargo_reason', 'taxi_reason', '2020-02-03 16:33:54.827958+03', false, true, true, '{}'::jsonb, '2020-02-03 16:33:54.827958+03'),
(4, '9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'taxi-order', 'park', 'driver', 'cargo_reason', 'taxi_reason', '2020-02-03 16:33:54.827958+03', true, true, true, '{}'::jsonb, '2020-02-03 16:33:54.827958+03');

INSERT INTO cargo_orders.orders_performers
(order_id, order_alias_id, phone_pd_id, name, driver_id, park_id, park_clid, car_id, car_number, car_model, lookup_version)
VALUES
(
    '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    '1234',
    '7930a74c2aa64f71b96dff9a91ea0b81',
    'abc',
    'driver',
    'park',
    'clid',
    'car',
    'car_number',
    'car_model',
    1
);
