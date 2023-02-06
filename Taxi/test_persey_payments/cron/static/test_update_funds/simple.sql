INSERT INTO persey_payments.fund
    (
        fund_id,
        name,
        offer_link,
        operator_uid,
        balance_client_id,
        trust_partner_id,
        trust_product_id,
        applepay_country_code,
        applepay_item_title
    )
VALUES
    (
        'deleted_fund',
        'Имя удаленного фонда',
        'http://fund.com',
        '777',
        'client1',
        'partner_id1',
        'product_id1',
        NULL,
        NULL
    ),
    (
        'updated_fund',
        'Старое имя',
        'old_offer_link',
        '777',
        'client2',
        'partner_id2',
        'product_id2',
        'en',
        'persey-payments.applepay.item_title.updated_fund'
    );
