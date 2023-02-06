insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data)
values ('123456', 'some_ext_id', now(), 'payment_not_received', 'complete', '{"payment": "not received"}');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, external_id, kind, business_rules_id,
                                                   transaction_date, external_payment_id, client_id, product_type,
                                                   amount, currency, status, data)
values (1, '1234567', 'auto_1', 'payment', '', now(), 'unpaid_1', '1', 'product', 200, 'RUB', 'complete', $$
{
    "version": "2",
    "payment": {
        "amount": "200",
        "currency": "RUB",
        "product_id": "product/retail/native",
        "product_type": "retail",
        "payment_method": "payment_not_received",
        "payment_service": "yaeda"
    },
    "client": {
        "id": "1"
    },
    "transaction_date": "2021-04-14T09:22:00+00:00",
    "external_payment_id": "unpaid_1"
}$$),
       (1, '1234567', 'auto_2', 'refund', '', now(), 'unpaid_1', '1', 'product', 1000, 'RUB', 'complete', $$
       {
           "version": "2",
           "refund": {
               "amount": "100",
               "currency": "RUB",
               "product_id": "product/retail/native",
               "product_type": "retail",
               "payment_method": "payment_not_received",
               "payment_service": "yaeda",
               "payment_terminal_id": "terminal_1"
           },
           "client": {
               "id": "1"
           },
           "transaction_date": "2021-04-14T09:22:00+00:00",
           "external_payment_id": "unpaid_1"
       }$$);
