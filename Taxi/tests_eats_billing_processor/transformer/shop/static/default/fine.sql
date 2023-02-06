insert into eats_billing_processor.fines(order_nr, client_id, fine_reason, actual_amount, calculated_amount, currency,
                                         fine_billing_date, external_id, external_payment_id, fine_reason_id)
values ('123456', '123456', 'cancel', '10.00', '10.00', 'RUB', '2021-03-24T12:11:00+00:00', '123456/1', '1', 1);
