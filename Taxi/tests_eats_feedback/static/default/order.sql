INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id)
VALUES

('210318-483588', '2021-02-10 12:23', 'finished', 'Alice'),

-- previously filled feedback
('100', '2021-02-10 12:23', 'finished', '111'),

-- previously cancelled feedback
('101', '2021-02-10 12:23', 'finished', '222');

-- id-s 100+ are reserved for feedbacks created in tests
