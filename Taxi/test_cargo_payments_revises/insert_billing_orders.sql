INSERT INTO 
    cargo_finance.billing_orders_revise_queue (
        id,
        received,
        source,
        kind,
        topic,
        order_document,
        migration_name
    )
VALUES
    (-9, now() - '1 day'::interval, 'cargo-finance', 'b2b_user_payment', 'taxi/user_on_delivery_payment/1', '{"payload": 1}', 'ndd'),
    (-8, now() - '2 day'::interval, 'cargo-payments', 'b2b_user_payment', 'taxi/user_on_delivery_payment/2', '{"payload": 2}', 'ndd'),
    (-7, now() - '3 day'::interval, 'cargo-payments', 'b2b_user_payment', 'taxi/user_on_delivery_payment/3', '{"payload": 3}', 'ndd'),
    (-6, now() - '4 day'::interval, 'cargo-finance', 'b2b_user_payment', 'taxi/user_on_delivery_payment/4', '{"payload": 4}', 'ndd'),
    (-5, now() - '0 day'::interval, 'cargo-finance', 'b2b_user_payment', 'taxi/user_on_delivery_payment/5', '{"payload": 5}', 'ndd'),
    (-4, now() - '0 day'::interval, 'cargo-finance', 'b2b_user_payment', 'taxi/user_on_delivery_payment/6', '{"payload": 6}', 'ndd'),
    (-3, now() - '1 day'::interval, 'cargo-payments', 'b2b_user_payment', 'taxi/user_on_delivery_payment/5', '{"payload": 5}', 'ndd')
