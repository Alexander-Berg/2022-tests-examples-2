INSERT INTO persey_payments.fund
    (
        fund_id,
        name,
        offer_link,
        operator_uid,
        balance_client_id,
        trust_partner_id,
        trust_product_id
    )
VALUES
    (
        'some_fund',
        'Имя фонда',
        'http://fund.com',
        '777',
        'some_client',
        'some_partner_id',
        'some_product_id'
    ),
    (
        'applepay_fund',
        'Имя фонда',
        'http://fund.com',
        '777',
        'some_client',
        'some_partner_id',
        'some_product_id'
    );

INSERT INTO persey_payments.ride_subs_order_cache
    (
        order_id,
        mod,
        fund_id
    )
VALUES
    (
        'order1',
        10,
        'applepay_fund'
    ),
    (
        'order2',
        10,
        'some_fund'
    ),
    (
        'order3',
        10,
        'some_fund'
    );

INSERT INTO persey_payments.ride_subs_paid_order
    (
        order_id,
        amount
    )
VALUES
    (
        'order2',
        '12345'
    );
