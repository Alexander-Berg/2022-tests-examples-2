INSERT INTO eats_proactive_support.order_cancellations 
(order_nr, cancellation_code, cancellation_caller, cancelled_at)
VALUES ('123', 'courier.unable_to_find', 'caller', NOW()),
('124', 'courier.busy', 'caller', NOW()),
('126', 'courier.unable_to_find', 'caller', NOW());
