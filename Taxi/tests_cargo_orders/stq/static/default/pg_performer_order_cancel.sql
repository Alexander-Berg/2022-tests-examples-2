INSERT INTO cargo_orders.orders
(commit_state, order_id, waybill_ref, provider_order_id, provider_user_id, use_cargo_pricing)
VALUES
    ('done', '9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'waybill-ref', 'taxi-order', 'taxi_user_id_1', true);

INSERT INTO cargo_orders.performer_order_cancel
(cargo_order_id, taxi_order_id, park_id, driver_id, cargo_cancel_reason, taxi_cancel_reason, created_ts, completed, guilty, need_reorder, payload, updated_ts)
VALUES
    ('9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'taxi-order', 'park', 'driver', 'cargo_reason', 'taxi_reason', '2020-02-03 16:33:54.827958+03', false, true, true, '{}'::jsonb, '2020-02-03 16:33:54.827958+03');

