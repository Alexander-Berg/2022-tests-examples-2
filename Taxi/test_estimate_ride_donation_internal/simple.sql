INSERT INTO persey_payments.ride_subs_order_cache
    (
        order_id,
        mod
    )
VALUES
    (
        'order1',
        10
    ),
    (
        'order2',
        10
    ),
    (
        'order2',
        NULL
    ),
    (
        'order4',
        10
    );

INSERT INTO persey_payments.ride_subs_paid_order
    (
        order_id,
        amount
    )
VALUES
    (
        'order4',
        '12345'
    );
