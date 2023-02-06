INSERT INTO orders
(
    id, idempotency_key, user_id, terminal_id,  created_at, updated_at, cancel_token, amount, status, items
)
VALUES
('order_1', 'ik_1', 1, 'terminal_id', '2022-02-01 00:00:00', '2022-02-01 00:02:00', 'cancel_token', 100, 'completed', '[{"tin": "", "vat": "nds_0", "price": "100.0", "title": "Мороженое", "quantity": "1.0"}]');


INSERT INTO admin_comments
(
    id, order_id, author, comment,  idempotency_key, created_at, deleted_at
)
VALUES
('comment_1', 'order_1', 'username', 'hello world', 'ik_1', '2022-02-01 00:01:00Z', '2022-02-01 00:01:30Z'),
('comment_2', 'order_1', 'username', 'hello world', 'ik_2', '2022-02-01 00:02:00Z', null),
('comment_3', 'order_1', 'username', 'hello world', 'ik_3', '2022-02-01 00:03:00Z', null);
