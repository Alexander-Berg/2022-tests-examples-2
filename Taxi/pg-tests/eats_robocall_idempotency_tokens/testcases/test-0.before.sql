INSERT INTO eats_robocall.idempotency_tokens
(token, call_id, updated_at)
VALUES
('token-1', 1, '2021-05-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
('token-2', 2, '2021-06-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
('token-3', 3, '2021-07-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
('token-4', 4, '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
