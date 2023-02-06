INSERT INTO eats_picker_orders.currencies
    (okv_code, okv_str, okv_name, sign)
VALUES (1, 'RUB', 'RUB', 'p');

INSERT INTO eats_picker_orders.orders (eats_id, place_id, picker_id,
                                       picker_card_type, picker_card_value,
                                       payment_value, payment_currency_id,
                                       payment_limit, comment, state, receipt)
VALUES ('test_eats_id', 0, 'test_picker_id', 'TinkoffBank', 'test_cid_1',
        1, 1, '1100.00', 'comment', 'picked_up', '{}'::JSONB),
       ('test_eats_id_paid', 0, 'test_picker_id_paid', 'TinkoffBank', 'test_cid_1',
        1, 1, '1100.00', 'comment', 'paid', '{}'::JSONB),
       ('test_eats_id_with_receipt', 0, 'test_picker_id_with_receipt', 'TinkoffBank', 'test_cid_1',
        1, 1, '1100.00', 'comment', 'picked_up',
        '{"t": "20200618T105208","s": "1098.02","fn": "4891689280440300","i": "19097","fp": "313667667","n": "1"}'::JSONB);
