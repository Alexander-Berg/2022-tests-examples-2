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
    client_ip,
    status
)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa00', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d20', '100', 'RUB', 'wallet_id', 'public_agreement_id', 'token1', 'trust1', 'session_uuid', 'client_ip', 'CREATED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d21', '101', 'RUB', 'wallet_id', 'public_agreement_id', 'token2', 'trust2', 'session_uuid', 'client_ip', 'PAYMENT_RECEIVED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d22', '102', 'RUB', 'wallet_id', 'public_agreement_id', 'token3', 'trust3', 'session_uuid', 'client_ip', 'FAILED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d23', '103', 'RUB', 'wallet_id', 'public_agreement_id', 'token4', 'trust4', 'session_uuid', 'client_ip', 'REFUNDED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d24', '104', 'RUB', 'wallet_id', 'public_agreement_id', 'token5', 'trust5', 'session_uuid', 'client_ip', 'REFUNDING'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa05', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d25', '105', 'RUB', 'wallet_id', 'public_agreement_id', 'token6', 'trust6', 'session_uuid', 'client_ip', 'FAILED_SAVED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa06', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d26', '106', 'RUB', 'wallet_id', 'public_agreement_id', 'token7', 'trust7', 'session_uuid', 'client_ip', 'REFUNDED_SAVED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa07', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d27', '107', 'RUB', 'wallet_id', 'public_agreement_id', 'token8', 'trust8', 'session_uuid', 'client_ip', 'SUCCESS_SAVED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa08', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d28', '108', 'RUB', 'wallet_id', 'public_agreement_id', 'token9', 'trust9', 'session_uuid', 'client_ip', 'CLEARING'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa09', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d29', '109', 'RUB', 'wallet_id', 'public_agreement_id', 'token10', 'trust10', 'session_uuid', 'client_ip', 'CLEARED'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d37', '110', 'RUB', 'wallet_id', 'public_agreement_id', 'token11', 'trust11', 'session_uuid', 'client_ip', 'FAILED_SAVING'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d38', '111', 'RUB', 'wallet_id', 'public_agreement_id', 'token12', 'trust12', 'session_uuid', 'client_ip', 'REFUNDED_SAVING'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12', '52f542ed-5813-4c96-9775-3a40e4f8b490', 'yandex_uid', 'e1c503af-bf18-4b0a-872b-bc007e6b4d39', '112', 'RUB', 'wallet_id', 'public_agreement_id', 'token13', 'trust113', 'session_uuid', 'client_ip', 'SUCCESS_SAVING')
;
