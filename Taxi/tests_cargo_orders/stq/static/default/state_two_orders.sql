INSERT INTO cargo_orders.orders
    (commit_state, order_id, waybill_ref, provider_order_id, provider_user_id, use_cargo_pricing)
VALUES
    ('done', '9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'waybill-ref', 'taxi-order', 'taxi_user_id_1', true),
    ('done', 'b65ad669-e067-406d-aac7-79fec6381f4a', 'waybill-ref-2', 'taxi-order-2', 'taxi_user_id_1', true);
