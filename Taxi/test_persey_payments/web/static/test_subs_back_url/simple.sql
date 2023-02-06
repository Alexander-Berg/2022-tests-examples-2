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
        '123',
        '1M',
        '8D',
        '1D',
        'some_subs_product_id'
    );

INSERT INTO persey_payments.subs
    (
        external_id,
        subs_product_id,
        fund_id,
        yandex_uid,
        user_name,
        user_email,
        trust_order_id,
        status
    )
VALUES
    (
        'some_external_id',
        1,
        'some_fund',
        '41',
        'some_user_name',
        'some_email',
        'some_order_id',
        'in_progress'
    );

INSERT INTO persey_payments.donation
    (
        fund_id,
        sum,
        yandex_uid,
        user_name,
        user_email,
        purchase_token,
        trust_order_id,
        subs_id,
        status
    )
VALUES
    (
        'some_fund',
        '123',
        '41',
        'some_user_name',
        'some_user_email',
        'trust-basket-token',
        'some_order_id',
        1,
        'finished'
    );
