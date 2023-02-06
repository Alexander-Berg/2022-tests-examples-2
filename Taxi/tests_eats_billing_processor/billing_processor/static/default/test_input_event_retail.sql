insert into eats_billing_processor.input_events (id, order_nr, external_id, event_at, kind, data, status, rule_name)
values (2, '123456-654321', 'some_event/1', now(), 'billing_payment', '{"test": "just for test"}', 'complete', 'retail');
