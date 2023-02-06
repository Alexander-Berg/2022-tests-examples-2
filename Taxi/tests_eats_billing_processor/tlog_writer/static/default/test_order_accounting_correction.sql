insert into eats_billing_processor.input_events (order_nr, external_id, event_at, kind, data, status)
values ('123456-654321', 'some_event/1', '2019-01-01T12:00:00+0000', 'billing_payment', '{"test": "just for test"}', 'complete');

insert into eats_billing_processor.order_accounting_correction(
    id,
    order_nr,
    login,
    ticket,
    amount,
    currency,
    correction_type,
    correction_group,
    product,
    detailed_product,
    created_at,
    transactions_count)
values  (1,
        '123456-654321',
        'aklevosh',
        'ticket',
        '20',
        'RUB',
        'commission_marketplace',
        'payment',
        'eats_account_correction',
        'eats_account_correction',
        '2022-03-31T00:00:00+0300',
        1);
