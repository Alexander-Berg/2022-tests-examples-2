INSERT INTO eats_picker_orders.currencies
    (okv_code, okv_str, okv_name, sign)
VALUES (1, 'RUB', 'RUB', 'p');

INSERT INTO eats_picker_orders.orders (eats_id, place_id, picker_id,
                                       picker_card_type, picker_card_value,
                                       payment_value, payment_currency_id,
                                       payment_limit, comment, flow_type, state, receipt)
VALUES ('test_eats_id', 0, 'test_picker_id', 'TinkoffBank', 'test_cid_1',
        1, 1, '1100.00', 'comment', 'picking_only', 'picked_up', '{}'::JSONB);
