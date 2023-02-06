insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data, rule_name)
values ('210405-000001', 'some_ext_id', now(), 'payment_received', 'complete', $$
{
  "external_payment_id" : "external_payment_id_1",
  "amount": "99",
  "client_id": "123456",
  "counteragent_id": "127054",
  "currency": "RUB",
  "event_at": "2020-12-17T10:53:44Z",
  "flow_type": "native",
  "order_nr": "201217-305204",
  "order_type": "native",
  "payment_method": "card",
  "payment_terminal_id": "95426005",
  "product_id": "delivery__001",
  "product_type": "delivery",
  "transaction_date": "2021-07-10T09:22:00+00:00",
  "transaction_type": "payment"
}
    $$, 'retail');
