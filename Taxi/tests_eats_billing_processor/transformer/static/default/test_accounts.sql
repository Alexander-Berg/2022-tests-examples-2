insert into eats_billing_processor.input_events (id, order_nr, external_id, event_at, kind, data, status, rule_name)
values (5, '123456', 'ext_1', now(), 'order_gmv', '{}', 'complete', 'default');

insert into eats_billing_processor.accounts (order_nr, name, transaction_date, client_id, input_event_id, amount)
values ('123456', 'gmv', now(), '1111', 5, 100);
insert into eats_billing_processor.accounts_total (start_date, client_id, name, amount)
values (now(), '1111', 'gmv', 100);
