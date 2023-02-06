insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, data, status)
values ('123456-654321', 'some_event/1', '2019-01-01T12:00:00+0000', 'billing_payment', '{"test": "just for test"}', 'complete');
