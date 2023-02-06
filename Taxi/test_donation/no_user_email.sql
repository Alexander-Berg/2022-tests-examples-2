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
    );

INSERT INTO persey_payments.donation
    (
        id,
        fund_id,
        yandex_uid,
        sum,
        user_name,
        purchase_token,
        trust_order_id,
        status
    )
VALUES
    (
        1,
        'some_fund',
        '123',
        '123.123',
        'some_name',
        'trust-basket-token',
        'some_order_id',
        'cleared'
    );
