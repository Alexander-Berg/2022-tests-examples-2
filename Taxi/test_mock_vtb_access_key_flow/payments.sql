INSERT INTO maas.payments
    (
        payment_id,
        idempotency_token,
        maas_user_id,
        status,
        url
    )
VALUES
(
    'change_key_id_initiated',
    'initiated',
    'maas_user_id',
    'initiated',
    'https://m.taxi.taxi.yandex.ru/webview/maas-mock?source=pay&payment_id=success'
),
(
    'change_key_id_success',
    'success',
    'maas_user_id',
    'success',
    'https://m.taxi.taxi.yandex.ru/webview/maas-mock?source=pay&payment_id=success'
),
(
    'change_key_id_canceled',
    'canceled',
    'maas_user_id',
    'canceled',
    'https://m.taxi.taxi.yandex.ru/webview/maas-mock?source=pay&payment_id=canceled'
),
(
    'change_key_id_failed',
    'failed',
    'maas_user_id',
    'failed',
    'https://m.taxi.taxi.yandex.ru/webview/maas-mock?source=pay&payment_id=failed'
);
