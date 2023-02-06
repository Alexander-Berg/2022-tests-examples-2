INSERT INTO persey_payments.lab
    (
        lab_id,
        partner_uid,
        operator_uid,
        trust_product_id_delivery,
        trust_product_id_test,
        trust_partner_id,
        balance_client_id,
        balance_client_person_id,
        balance_contract_id,
        status
    )
VALUES
    (
        'some_lab',
        'partner_uid',
        'operator_uid',
        'trust_product_id_delivery',
        'trust_product_id_test',
        'trust_partner_id',
        'balance_client_id',
        'balance_client_person_id',
        'balance_contract_id',
        'ready'
    );


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
        'some_balance_client',
        'some_partner_id',
        'some_product_id'
    );
