--freshest order to require feedback
INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id)
VALUES
('210318-000000', '2020-07-23T13:00:00+00:00', 'finished', 'Alice');

--fresh order to require feedback
INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id)
VALUES
('210318-000001', '2020-07-23T12:00:00+00:00', 'finished', 'Alice');

--other eater
INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id)
VALUES
('210318-000004', '2020-07-23T11:59:00+00:00', 'finished', 'Bob');

--Not delivered order
INSERT INTO eats_feedback.orders
(order_nr, order_delivered_at, status, eater_id)
VALUES
('210318-000005', NULL, 'payed', 'Alice');
