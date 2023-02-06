insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data)
values ('123456', 'payment_1', '2021-04-05T08:25:00+00:00', 'additional_promo_payment', 'complete', '{}');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, event_at, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (1, '123456', '2021-04-05T08:25:00+00:00', '1/0', 'payment', '', now(), 'payment_1', '12345', 'product', 100.00, 'RUB', 'complete', $$
    {
    "payment": {
        "amount": "100.00",
        "currency": "RUB",
        "product_id": "some_product_weekly",
        "product_type": "product_weekly",
        "payment_method": "marketing",
        "payment_service": "yaeda"
    },
    "client": {
        "id": "12345"
    },
    "transaction_date": "2021-04-05T08:25:00+00:00",
    "external_payment_id": "payment_1",
    "rule": "marketplace",
    "version": "2.1"
}$$);
