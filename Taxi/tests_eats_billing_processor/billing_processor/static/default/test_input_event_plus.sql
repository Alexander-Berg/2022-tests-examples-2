insert into eats_billing_processor.input_events (id, order_nr, external_id, event_at, kind, data, status)
values (1, '123456-654321', 'some_event/1', now(), 'plus_cashback_emission', '{"test": "just for test"}', 'complete'),
       (2, '123456-654321', 'some_event/2', now(), 'payment_update_plus_cashback', '{"test": "just for test"}', 'complete');
