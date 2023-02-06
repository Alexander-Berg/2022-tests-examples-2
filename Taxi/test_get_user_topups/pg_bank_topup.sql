INSERT INTO bank_topup.payments(
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
VALUES
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d20', '100', 'RUB', 'wallet_id', 'public_agreement_id', 'token1', 'trust1', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d21', '101', 'RUB', 'wallet_id', 'public_agreement_id', 'token2', 'trust2', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d22', '102', 'RUB', 'wallet_id', 'public_agreement_id', 'token3', 'trust3', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d23', '103', 'RUB', 'wallet_id', 'public_agreement_id', 'token4', 'trust4', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d24', '104', 'RUB', 'wallet_id', 'public_agreement_id', 'token5', 'trust5', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d25', '105', 'RUB', 'wallet_id', 'public_agreement_id', 'token6', 'trust6', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d26', '106', 'RUB', 'wallet_id', 'public_agreement_id', 'token7', 'trust7', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d27', '107', 'RUB', 'wallet_id', 'public_agreement_id', 'token8', 'trust8', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d28', '108', 'RUB', 'wallet_id', 'public_agreement_id', 'token9', 'trust9', 'session_uuid', 'client_ip'),
    ('bank_uid', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d29', '109', 'RUB', 'wallet_id', 'public_agreement_id', 'token10', 'trust10', 'session_uuid', 'client_ip')
;
