insert into payments.payments(
    amount,
    client_id,
    contract_id,
    currency,
    firm_id,
    payment_processor,
    payment_type,
    person_id,
    source_id,
    source_type,
    dry_run
) values
(
    '500.00',
    '1349515601',
    '3697999',
    'RUB',
    13,
    'YA_BANK',
    'PAYMENT_REQUIREMENT',
    '123',
    'c4ca4238a0b923820dcc509a6f75849b',
    'TAXI',
    false
);


insert into payments.payment_event_log(
    payment_id,
    amount,
    amount_applied,
    idempotency_key,
    external_payment_id,
    status,
    updates
) values
(
    1,
    '500.00',
    '0.00',
    'NEW',
     NULL,
    'NEW',
    '{"pro_payload": { "pro_category_id": "PAYMENT_REQUIREMENT", "pro_order_id": "6d5144addb183c86acee401124cb2c1f"}, "payment_group": "REVENUE", "account": "ЛСТ-12345678"}'::jsonb
);
