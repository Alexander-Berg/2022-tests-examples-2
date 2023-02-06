insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, status, data)
values ('123456', 'some_ext_id', '2021-03-24T12:11:00+00:00', 'payment_not_received', 'complete',
        '{"payment": "not received"}'),
       ('123456', 'some_ext_id2', '2021-03-24T12:12:00+00:00', 'payment_not_received', 'complete',
        '{"payment": "not received"}');

insert into eats_billing_processor.billing_events (input_event_id, order_nr, kind, event_at, transaction_date,
                                                   external_payment_id, external_id, data, client_id, product_type,
                                                   amount, currency)
values (1, '123456', 'refund', '2021-03-23T12:11:00+00:00', '2021-03-24T12:11:00+00:00', 'ext_id', 'ext_id', $$
{
    "transaction_date": "2021-03-23T12:11:00+00:00",
    "external_payment_id": "ext_id",
    "client": {
        "id": "1"
    },
    "refund": {
        "amount": "200",
        "currency": "RUB",
        "product_id": "product/retail/native",
        "product_type": "retail",
        "payment_method": "payment_not_received",
        "payment_service": "yaeda"
    },
    "version": "2"
}$$,
        '3', 'product', '200', 'RUB'),
       (2, '123456', 'refund', '2021-03-24T12:14:00+00:00', '2021-03-24T12:14:00+00:00', 'ext_id2', 'ext_id2', $$
       {
           "transaction_date": "2021-03-24T12:14:00+00:00",
           "external_payment_id": "ext_id2",
           "client": {
               "id": "3"
           },
           "refund": {
               "amount": "300",
               "currency": "RUB",
               "product_id": "product/native/native",
               "product_type": "product",
               "payment_method": "payment_not_received",
               "payment_service": "yaeda"
           },
           "version": "2"
       }$$,
        '3', 'product', '300', 'RUB');

insert into eats_billing_processor.fines (order_nr, client_id, fine_reason, fine_reason_id,
                                          actual_amount, calculated_amount, currency, fine_billing_date,
                                          external_id, external_payment_id)
values ('123456', '3', 'cancel', 2, '200', '150', 'RUB', now(), '5', 'ext_id'),
       ('123456', '3', 'refund', 2, '300', '250', 'RUB', now(), '6', 'ext_id2');
