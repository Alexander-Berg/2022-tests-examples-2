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
        'friends',
        'Имя фонда',
        'http://fund.com',
        '777',
        'client1',
        'partner_id1',
        'product_id1'
    );

INSERT INTO persey_payments.ride_subs
    (
        yandex_uid,
        brand,
        fund_id,
        mod,
        locale
    )
VALUES
    (
        'market_uid',
        'market',
        'friends',
        10,
        'en'
    );

INSERT INTO persey_payments.active_ride_subs
    (
        ride_subs_id,
        yandex_uid,
        brand
    )
VALUES
    (
        1,
        'market_uid',
        'market'
    );
