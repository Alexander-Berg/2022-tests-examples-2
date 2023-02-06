insert into eats_billing_processor.input_events (id, order_nr, external_id, event_at, kind, status, data)
values (5, '210405-000001', 'some_ext_id', now(), 'payment_received', 'complete', '{"payment": "received"}');

insert into eats_billing_processor.accounts(order_nr, name, transaction_date, client_id, input_event_id, amount)
values ('123456', 'gmv', now(), '123456', 5, '1200')

