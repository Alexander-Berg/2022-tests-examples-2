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
        '2017-09-04 23:10:00.00+00:00'
    ),
    (
        'order2',
        10,
        '2017-09-04 23:11:00.00+00:00'
    );

INSERT INTO persey_payments.ride_subs_order_user
    (
        yandex_uid,
        brand,
        order_id,
        created_at
    )
VALUES
    (
        'phonish_uid',
        'yataxi',
        'order3',
        '2017-09-04 23:10:00.00+00:00'
    ),
    (
        'portal_uid',
        'yataxi',
        'order4',
        '2017-09-04 23:11:00.00+00:00'
    );


INSERT INTO persey_payments.ride_subs_paid_order
    (
        order_id,
        amount,
        created_at
    )
VALUES
    (
        'order5',
        '5',
        '2017-09-03 13:09:19.00+00:00'
    ),
    (
        'order6',
        '5',
        '2017-09-03 13:09:20.00+00:00'
    );
