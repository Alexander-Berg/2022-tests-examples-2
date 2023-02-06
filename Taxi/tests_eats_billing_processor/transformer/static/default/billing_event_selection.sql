insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data, rule_name)
values ('201217-305204', 'some_ext_id', now(), 'payment_received', 'complete', $$
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

insert into eats_billing_processor.billing_events (id, input_event_id, order_nr, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (8, 1, '201217-305204', '1/0', 'commission', 'N/A', '2021-03-24T12:11:00+00:00', 'external_id_1', '123456', 'product', 100, 'RUB', 'new', $$
{
    "commission": {
        "amount": "100",
        "currency": "RUB",
        "product_id": "some_product_id",
        "product_type": "product"
    },
    "client": {
        "id": "123456",
        "contract_id": "test_contract_id"
    },
    "transaction_date": "2021-07-10T09:22:00+00:00",
    "external_payment_id": "external_id_1",
    "rule": "retail",
    "version": "2.1"
}$$);
