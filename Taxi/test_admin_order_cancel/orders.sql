INSERT INTO orders
(
    id, idempotency_key, user_id, terminal_id,  created_at, updated_at, cancel_token, amount, status, is_cancelling, items
)
VALUES
('order_1', 'ik_1', 1, 'terminal_id', '2022-02-01 00:00:00', '2022-02-01 00:02:00', 'cancel_token', 100, 'new', null, '[{"tin": "", "vat": "nds_0", "price": "100.0", "title": "Мороженое", "quantity": "1.0"}]'),
('order_2', 'ik_2', 1, 'terminal_id', '2022-02-02 00:00:00', '2022-02-02 00:02:00', 'cancel_token', 100, 'failed', false, '[{"tin": "", "vat": "nds_0", "price": "100.0", "title": "Мороженое", "quantity": "1.0"}]'),
('order_3', 'ik_3', 1, 'terminal_id', '2022-02-03 00:00:00', '2022-02-03 00:02:00', 'cancel_token', 100, 'failed', true, '[{"tin": "", "vat": "nds_0", "price": "100.0", "title": "Мороженое", "quantity": "1.0"}]');
