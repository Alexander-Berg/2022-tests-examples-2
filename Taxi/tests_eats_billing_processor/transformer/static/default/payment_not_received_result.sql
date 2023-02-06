insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data)
values ('210405-000001', 'payment_1', now(), 'payment_not_received', 'complete', '{"payment": "not received"}');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (1, '210405-000001', 'payment_1', 'payment', '', now(), 'payment_1', '1234', 'product', 150.55, 'RUB', 'complete', $$
    {
    "version": "2",
        "payment": {
        "amount": "150.55",
        "currency": "RUB",
        "product_id": "product/native_weekly",
        "product_type": "product_weekly",
        "payment_method": "payment_not_received",
        "payment_service": "yaeda"
    },
    "client": {
        "id": "1234"
    },
    "transaction_date": "2021-04-14T09:22:00+00:00",
    "external_payment_id": "payment_1"
}$$);
