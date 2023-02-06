INSERT INTO persey_payments.order
    (order_id, payment_method_id, need_free, status)
VALUES
    ('first', 'card-first', FALSE, 'in_progress'),
    ('second', 'card-second', FALSE, 'in_progress');

INSERT INTO persey_payments.basket
    (
        purchase_token, order_id, mark, test_cost, delivery_cost, trust_payment_id,
        trust_order_id_test, trust_order_id_delivery, user_uid, status, payout_ready_dt,
        created_at
    )
VALUES
    ('1', 'first', '1', '123', '321', 'a', 'oid_test_a', 'oid_delivery_a', '123',
     'delivered', '2017-09-08 00:00:00.00+00:00', '2017-09-05 01:00:00.00+00:00'),
    ('2', 'first', '2', '123', '321', 'b', 'oid_test_b', 'oid_delivery_b', '123',
     'started', NULL, '2017-09-05 01:00:00.00+00:00'),
    ('3', 'first', '3', '123', '321', 'c', 'oid_test_c', 'oid_delivery_c', '123',
     'delivered', '2017-09-08 01:00:00.00+00:00', '2017-09-05 01:00:00.00+00:00'),
    ('4', 'second', '1', '123', '321', 'd', 'oid_test_d', 'oid_delivery_d', '123',
     'delivered', '2017-09-08 02:00:00.00+00:00', '2017-09-06 01:00:00.00+00:00'),
    ('5', 'second', '2', '123', '321', 'e', 'oid_test_e', 'oid_delivery_e', '123',
     'delivered', '2017-09-08 03:00:00.00+00:00', '2017-09-06 01:00:00.00+00:00'),
    ('6', 'second', '3', '123', '321', 'f', 'oid_test_f', 'oid_delivery_f', '123',
     'delivered', '2017-09-08 04:00:00.00+00:00', '2017-09-06 01:00:00.00+00:00');
