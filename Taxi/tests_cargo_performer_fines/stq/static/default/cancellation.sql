INSERT INTO cargo_performer_fines.cancellations
(cancel_id, cargo_order_id, taxi_order_id, park_id, driver_id, cargo_cancel_reason, guilty, payload)
VALUES
(1, 'c8979166-e428-43be-8b37-5ea1c958debb', 'taxi', 'park_id_1', 'driver_id_1', 'reason', True, '{}'::jsonb);
