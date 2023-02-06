insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, data, status)
values ('123456-654321', 'some_event/1', now(), 'billing_payment', '{"test": "just for test"}', 'complete');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (1, '210405-000001', '2/0', 'payment', '', now(), 'payment_1', '5678', 'delivery', 150.55, 'RUB', 'new', $$
{
    "payment": {
        "amount": "150.55",
        "currency": "RUB",
        "product_id": "delivery__001",
        "product_type": "delivery",
        "payment_method": "card"
    },
    "client": {
        "id": "5678"
    },
    "transaction_date": "2021-04-05T08:25:00+00:00",
    "external_payment_id": "payment_1",
    "version": "2"
}$$);

insert into eats_billing_processor.transfers (billing_event_id, service_order_id, kind, service_id, dt, orig_id,
                                              client_id, paysys_partner_id, payment_type, product, amount, currency,
                                              geo_hierarchy, business, external_id)
values (1, '210405-000001', 'payment', 645, now(), NULL, '5678', 'alfa', 'card', 'delivery', 150.55, 'RUB', NULL, NULL,
        '2/0');
