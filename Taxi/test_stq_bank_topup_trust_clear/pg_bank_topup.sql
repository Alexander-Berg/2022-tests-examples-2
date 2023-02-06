INSERT INTO bank_topup.payments(
    payment_id,
    bank_uid,
    yandex_uid,
    idempotency_token,
    amount,
    currency,
    wallet_id,
    public_agreement_id,
    purchase_token,
    trust_payment_id,
    session_uuid,
    client_ip
)
VALUES (
    'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df',
    'bank_uid',
    'yandex_uid',
    'e1c503af-bf18-4b0a-872b-bc007e6b4d20',
    '100',
    'RUB',
    'wallet_id',
    'public_agreement_id',
    'purchase_token',
    'trust_payment_id_1',
    'session_uuid',
    'client_ip'
);
