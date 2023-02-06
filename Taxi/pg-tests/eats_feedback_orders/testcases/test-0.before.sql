INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id, updated_at)
VALUES
('100000-100000', NOW(), 'finished', 'id1', '2021-12-04T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100001-100000', NOW(), 'finished', 'id2', '2021-12-05T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100011-100000', NOW(), 'finished', 'id3', '2021-12-11T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100111-100000', NOW(), 'finished', 'id4', '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
