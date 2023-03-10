INSERT INTO eats_tips_payments.orders (
    order_id,
    amount,
    yandex_user_id,
    user_ip,
    user_has_plus,
    plus_amount,
    cashback_status,
    is_refunded,
    system_income,
    id,
    order_id_b2p,
    idempotency_token,
    recipient_id,
    recipient_id_b2p,
    is_guest_commission,
    commission,
    guest_amount,
    recipient_amount,
    payment_type,
    status,
    status_b2p,
    review_id,
    created_at
)
VALUES
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_1',
    '101',
    'idempotency_token_1',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 00:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_2',
    '102',
    'idempotency_token_2',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 19:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_3',
    '103',
    'idempotency_token_3',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'AUTHORIZE_FAILED',
    'REGISTERED',
    '100',
    '2022-02-17 00:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_4',
    '104',
    'idempotency_token_4',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 00:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_5',
    '105',
    'idempotency_token_5',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 00:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_6',
    '106',
    'idempotency_token_6',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-03 18:59:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_7',
    '107',
    'idempotency_token_7',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 00:00:00'
),
(
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    'order_id_8',
    '108',
    'idempotency_token_8',
    '',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETE_FAILED',
    'AUTHORIZED',
    '100',
    '2022-02-17 00:00:00'
);

INSERT INTO eats_tips_payments.orders_retries (
    order_id,
    tries,
    next_try
)
VALUES
(
    'order_id_4',
    1,
    '2022-02-17 18:59:00+0000'
),
(
    'order_id_7',
    1,
    '2022-02-17 19:01:00+0000'
),
(
    'order_id_8',
    5,
    '2022-02-17 18:59:00+0000'
);
