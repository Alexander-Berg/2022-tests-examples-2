insert into eats_billing_processor.fines(order_nr, client_id, fine_reason, fine_reason_id, actual_amount,
                                         calculated_amount, currency, fine_billing_date, external_id,
                                         external_payment_id)
values ('123456', 'client_id_1', 'refund', 1, '12.33', '2.33', 'RUB', '2021-04-14T09:22:00+00:00', 'external_id', '1'),
       ('12345', 'client_id_1', 'refund', 2, '12.33', '2.33', 'RUB', '2021-04-14T09:22:00+00:00', 'external_id1', '2'),
       ('12345', 'client_id_1', 'cancel', 1, '12.33', '2.33', 'RUB', '2021-04-14T09:22:00+00:00', 'external_id2', '3');

insert into eats_billing_processor.appeals(fine_id, amount, ticket)
values (2, '10', 'test');
