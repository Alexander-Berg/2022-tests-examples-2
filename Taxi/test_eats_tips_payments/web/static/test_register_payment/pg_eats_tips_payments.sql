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
    round_profit
) VALUES (
    NULL,
    50,
    NULL,
    '1.2.3.4',
    NULL,
    NULL,
    NULL,
    FALSE,
    NULL,
    '5e65dc9f-f9f3-4306-9476-cb2691e1af56',
    NULL,
    'idempotency_token_1',
    '00000000-0000-0000-0000-000000000001',
    '',
    FALSE,
    3,
    50,
    47,
    'apple_pay_b2p',
    'COMPLETED',
    'COMPLETED',
    '100',
    0
);

INSERT INTO eats_tips_payments.money_box_periods
(
    money_box_id,
    period_start,
    period_end,
    balance,
    closed
)
VALUES
(
'20000000-0000-0000-0000-000000000200',
'1970-01-01T03:00:00+03:00',
'2970-01-01T03:00:00+03:00',
0,
false
);

INSERT INTO eats_tips_payments.reviews(
    review_id
    , recipient_id
    , recipient_type
    , place_id
    , review
    , star
    , quick_choices
    , idempotency_token
    , created_at
)
VALUES
('review00-0000-0000-0000-cb2691e1af56', 'f907a11d-e1aa-4b2e-8253-069c58801727', 'partner', 'eef266b2-09b3-4218-8da9-c90928608d97', 'Text review 44', 4, '{service}', 'idempotency_token_44', '2021-10-10 04:30:00Z')
;
