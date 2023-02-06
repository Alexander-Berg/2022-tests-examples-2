INSERT INTO eats_tips_payments.money_box_periods (
    id,
    money_box_id,
    period_start,
    period_end,
    closed
)
VALUES
('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '2022-01-01', '2022-02-01', false),
('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', '2022-01-01', '2022-02-01', true)
;

INSERT INTO eats_tips_payments.transfer_idempotency_tokens(
    token,
    money_box_period_id
)
VALUES
('token2', '10000000-0000-0000-0000-000000000001')
;
