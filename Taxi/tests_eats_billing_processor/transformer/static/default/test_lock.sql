insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data)
values ('210405-000001', 'some_ext_id', now(), 'payment_received', 'complete', '{"payment": "received"}');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (1, '210405-000001', '2/0', 'payment', '', now(), 'payment_1', '5678', 'delivery', 150.55, 'RUB', 'new', $$
{
    "payment": {
        "amount": "150.55",
        "currency": "RUB",
        "product_id": "some_product",
        "product_type": "delivery",
        "payment_method": "card"
    },
    "client": {
        "id": "1234",
        "contract_id": "test_contract_id"
    },
    "transaction_date": "2021-04-05T08:25:00+00:00",
    "external_payment_id": "payment_1",
    "rule": "default",
    "version": "2.1"
}$$);
