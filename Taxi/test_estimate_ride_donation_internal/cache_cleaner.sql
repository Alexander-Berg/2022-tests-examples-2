INSERT INTO persey_payments.ride_subs_order_cache
    (
        order_id,
        mod,
        created_at
    )
VALUES
    (
        'order1',
        10,
        '2020-05-02 11:57:59.00+00:00'
    ),
    (
        'order2',
        10,
        '2020-05-02 11:58:00.00+00:00'
    );

INSERT INTO persey_payments.ride_subs_paid_order
    (
        order_id,
        amount,
        created_at
    )
VALUES
    (
        'order3',
        '54321',
        '2020-05-02 11:54:59.00+00:00'
    ),
    (
        'order4',
        '12345',
        '2020-05-02 11:55:00.00+00:00'
    );
