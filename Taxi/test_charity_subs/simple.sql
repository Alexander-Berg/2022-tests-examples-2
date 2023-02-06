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
        'common_fund',
        'Имя фонда',
        'http://fund.com',
        '777',
        'client1',
        'partner_id1',
        'product_id1'
    );

INSERT INTO persey_payments.subs_product
    (
        amount,
        period,
        retry_charging_limit,
        retry_charging_delay,
        trust_product_id
    )
VALUES
    (
        '100',
        '1M',
        '1D',
        '1D',
        'product_id1'
    );


INSERT INTO persey_payments.subs
    (
        external_id,
        subs_product_id,
        fund_id,
        user_name,
        user_email,
        trust_order_id,
        status,
        subs_until_ts,
        yandex_uid
    )
VALUES
    (
        '1',
        1,
        'common_fund',
        'alice',
        'alice@yandex.ru',
        'some_order_id',
        'in_progress',
        '2020-5-3'::TIMESTAMPTZ,
        '123456789'
    );
