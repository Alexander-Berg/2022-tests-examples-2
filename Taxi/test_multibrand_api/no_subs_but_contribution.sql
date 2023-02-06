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
        phone_id,
        brand,
        fund_id,
        mod,
        locale,
        hidden_at
    )
VALUES
    (
        'phonish_uid',
        'af35af35af35af35af35af35',
        'yataxi',
        'friends',
        10,
        'en',
        CURRENT_TIMESTAMP
    );


INSERT INTO persey_payments.donation
    (
        fund_id,
        yandex_uid,
        sum,
        status,
        ride_subs_id,
        brand,
        order_id
    )
VALUES
    (
        'friends',
        'phonish_uid',
        '321',
        'finished',
        1,
        'yataxi',
        'stub'
    );
