INSERT INTO cargo_trucks.payments(
    id,
    yt_line_num,
    cash_payment_id,
    amount,
    effective_date,
    trx_text,
    customer_text,
    currency,
    inn,
    payment_num,
    payment_date,
    yandex_account_num,
    trx_number,
    billing_person_id,
    creation_date,
    bik,
    account_name,
    oebs_export_req_id
)
VALUES (
    0,
    1,
    22,
    103.4,
    '2022-01-01T12:00:00Z',
    'trx1',
    'cstmr text',
    'RUB',
    '140000001',
    '1234',
    '2022-01-02T12:00:00Z',
    '5',
    '12345',
    '100',
    '2022-01-03T12:00:00Z',
    '100000001',
    'account',
    4321
),
(
    1,
    2,
    22,
    1009.89,
    '2022-01-01T12:00:00Z',
    'trx2',
    'cstmr text',
    'USD',
    '140000001',
    '1234',
    '2022-01-02T12:00:00Z',
    '5',
    '12345',
    '100',
    '2022-01-03T12:00:00Z',
    '100000001',
    'account',
    4321
),
(
    2,
    3,
    22,
    0.90,
    '2022-01-01T12:00:00Z',
    'trx3',
    'cstmr text',
    'RUB',
    '140000001',
    '1234',
    '2022-01-02T12:00:00Z',
    '5',
    '12345',
    '100',
    '2022-01-06T12:00:00Z',
    '100000001',
    'account',
    4321
),
(
    3,
    4,
    NULL,
    1.90,
    NULL,
    NULL,
    NULL,
    'RUB',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
);