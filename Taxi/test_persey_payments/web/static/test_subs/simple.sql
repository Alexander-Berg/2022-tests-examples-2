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
