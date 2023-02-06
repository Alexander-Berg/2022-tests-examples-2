INSERT INTO persey_payments.order
    (
        order_id,
        payment_method_id,
        need_free,
        status
    )
VALUES
    (
        'some_order',
        'some_payment_method',
        FALSE,
        'in_progress'
    );


INSERT INTO persey_payments.basket
    (
        purchase_token,
        order_id,
        mark,
        trust_payment_id,
        trust_order_id_delivery,
        trust_order_id_test,
        user_uid,
        test_cost,
        delivery_cost,
        hold_amount,
        status
    )
VALUES
    (
        'trust-basket-token',
        'some_order',
        'main',
        'trust-payment-id',
        'some_order_delivery',
        'some_order_test',
        'some_user_uid',
        '321',
        '123',
        '777.7',
        'delivered'
    );
