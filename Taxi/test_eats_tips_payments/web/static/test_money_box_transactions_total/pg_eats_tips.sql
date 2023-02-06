INSERT INTO eats_tips_payments.orders (
    created_at,
    order_id_b2p,
    idempotency_token,
    recipient_id,
    recipient_id_b2p,
    recipient_type,
    commission,
    amount,
    guest_amount,
    payment_type,
    payer_type,
    payer_id,
    status,
    status_b2p
)
VALUES
('2021-01-27 16:30', null, 'token1', '00000000-0000-0000-1000-000000000001', '00000000-0000-0000-1000-000000000001', 'partner', 0, 100, 100, 'b2p', 'MONEY_BOX', '00000000-0000-0000-0000-000000000001', 'CREATED', null),
('2021-01-27 16:35', 'b2p_id_1', 'token2', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'money_box', 0, 150, 150, 'b2p', 'CUSTOMER', null, 'COMPLETED', 'COMPLETED'),
('2021-01-27 16:40', 'b2p_id_2', 'token3', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'money_box', 0, 10000, 100, 'b2p', 'CUSTOMER', null, 'REGISTERED', 'REGISTERED'),
('2021-01-27 16:45', 'b2p_id_3', 'token4', '00000000-0000-0000-1000-000000000001', '00000000-0000-0000-1000-000000000001', 'partner', 0, 100, 100, 'b2p', 'MONEY_BOX', '00000000-0000-0000-0000-000000000001', 'COMPLETED', 'COMPLETED')
;
