INSERT INTO cargo_orders.orders_errors
(waybill_ref, cargo_order_id, reason, message, updated_ts)
VALUES
    ('waybill-ref', 'b1fe01dd-c302-4727-9f80-6e6c5e210a9f', 'COMMIT_ERROR', 'UNKNOWN_CARD', '2021-06-30T11:08:43.070017+00:00');

INSERT INTO cargo_orders.orders_errors
(waybill_ref, cargo_order_id, reason, message, updated_ts)
VALUES
    ('null-order-id', NULL, 'COMMIT_ERROR', 'UNKNOWN_CARD', '2021-06-30T11:08:43.070017+00:00');
