INSERT INTO eats_proactive_support.order_cancellations 
(order_nr, cancellation_code, cancellation_caller, cancelled_at)
VALUES
('125', 'courier.busy', 'caller', '2021-12-01T12:00:00.1234+03:00'::TIMESTAMPTZ),
('126', 'courier.unable_to_find', 'caller', '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
