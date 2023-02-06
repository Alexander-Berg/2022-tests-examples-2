BEGIN TRANSACTION;

INSERT INTO cart.carts (cart_id, cart_version, updated, created, user_type, user_id, promocode, idempotency_token, order_id, payment_method_type, payment_method_id, delivery_type, session, bound_sessions, status)
VALUES
('e6a59113-503c-4d3e-8c59-000000000010', 153, '2020-09-23 16:20:59.599808+03', '2020-09-22 18:48:09.353629+03', 'eats_user_id', '145597824', NULL, 'idempotency_token_from_SQL', NULL, 'card', 'card-x523dcaee05744ea75a8eeda7', 'eats_dispatch', 'taxi:73116a0a23844b5fbd5204ac028f99a5', '{taxi:z3c7ea3265a5434cad291289f9cd7d72}', 'editing'),
('e6a59113-503c-4d3e-8c59-000000000011', 153, '2020-09-23 16:20:59.599808+03', '2020-09-22 18:48:09.353629+03', 'eats_user_id', '145597824', NULL, 'idempotency_token_from_SQL', NULL, 'card', 'card-x523dcaee05744ea75a8eeda7', 'eats_dispatch', 'taxi:73116a0a23844b5fbd5204ac028f99a5', '{taxi:z3c7ea3265a5434cad291289f9cd7d72}', 'editing'),
('e6a59113-503c-4d3e-8c59-000000000012', 153, '2020-09-23 16:20:59.599808+03', '2020-09-22 18:48:09.353629+03', 'eats_user_id', '145597824', NULL, 'idempotency_token_from_SQL', NULL, 'card', 'card-x523dcaee05744ea75a8eeda7', 'eats_dispatch', 'taxi:73116a0a23844b5fbd5204ac028f99a5', '{taxi:z3c7ea3265a5434cad291289f9cd7d72}', 'editing');

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency, updated, created, full_price, title, reserved)
VALUES
('e6a59113-503c-4d3e-8c59-000000000010', 'd3fb22b6f07341358bff6fc69db13dfa000200010001', 119.0000, 1.0000, 'RUB', '2020-09-23 16:20:59.599808+03', '2020-09-23 16:20:59.599808+03', 119.0000, 'Капучино', NULL),
--('e6a59113-503c-4d3e-8c59-000000000010', 'd3fb22b6f07341358bff6fc69db13dfa000200010001', 104.0000, 1.0000, 'RUB', '2020-09-23 16:20:59.599808+03', '2020-09-23 16:20:59.599808+03', 104.0000, 'Половина арбуза Россия', NULL),
('e6a59113-503c-4d3e-8c59-000000000011', 'd3fb22b6f07341358bff6fc69db13dfa000200010001', 119.0000, 1.0000, 'RUB', '2020-09-23 16:20:59.599808+03', '2020-09-23 16:20:59.599808+03', 119.0000, 'Капучино', NULL),
('e6a59113-503c-4d3e-8c59-000000000012', 'd3fb22b6f07341358bff6fc69db13dfa000200010001', 119.0000, 1.0000, 'RUB', '2020-09-23 16:20:59.599808+03', '2020-09-23 16:20:59.599808+03', 119.0000, 'Капучино', NULL);

INSERT INTO cart.checkout_data (
    cart_id,
    depot_id,
    unavailable_checkout_reason,
    promocode,
    order_conditions_with_eta,
    order_conditions_total_time,
    order_conditions_cooking_time,
    order_conditions_delivery_time,
    cart_version,
    payment_method_discount,
    calculation_log,
    promocode_discount,
    promocode_properties,
    updated,
    depot_switch_time,
    depot_status
) VALUES
    (
        'e6a59113-503c-4d3e-8c59-000000000001',
        '71249',
        'no_reason',
        NULL,
        '(0.0000,25,15)',
        1,
        2,
        3,
        3,
        false,
        '{"total": "99", "coupon": {"value": "0"}, "currency": "RUB", "calculation": {"items": [{"id": "a1664e3e046044baab6d8c0fb2926c1c000100010001", "price": "99", "quantity": "1", "subtotal": "99", "discounts": [], "catalog_price": "99"}], "subtotal": "99"}, "service_fees": {"delivery_cost": "0"}, "discounts_response": {"match_results": [{"results": [{"status": "ok", "discounts": [], "hierarchy_name": "menu_discounts"}, {"status": "ok", "discounts": [], "hierarchy_name": "cart_discounts"}], "subquery_id": "a1664e3e046044baab6d8c0fb2926c1c000100010001"}]}}',
        NULL,
        NULL,
        '2020-09-18 10:56:04.128038+03',
        NULL,
        'available'
    ),
    (
        'e6a59113-503c-4d3e-8c59-000000000011',
        '71249',
        'no_reason',
        NULL,
        '(0.0000,25,15)',
        3,
        1,
        2,
        3,
        false,
        '{"total": "99", "coupon": {"value": "0"}, "currency": "RUB", "calculation": {"items": [{"id": "a1664e3e046044baab6d8c0fb2926c1c000100010001", "price": "99", "quantity": "1", "subtotal": "99", "discounts": [], "catalog_price": "99"}], "subtotal": "99"}, "service_fees": {"delivery_cost": "0"}, "discounts_response": {"match_results": [{"results": [{"status": "ok", "discounts": [], "hierarchy_name": "menu_discounts"}, {"status": "ok", "discounts": [], "hierarchy_name": "cart_discounts"}], "subquery_id": "a1664e3e046044baab6d8c0fb2926c1c000100010001"}]}}',
        NULL,
        NULL,
        '2020-09-18 10:56:04.128038+03',
        NULL,
        'available'
    ),
    (
        'e6a59113-503c-4d3e-8c59-000000000021',
        '71249',
        'no_reason',
        NULL,
        '(0.0000,25,15)',
        2,
        3,
        1,
        3,
        false,
        '{"total": "99", "coupon": {"value": "0"}, "currency": "RUB", "calculation": {"items": [{"id": "a1664e3e046044baab6d8c0fb2926c1c000100010001", "price": "99", "quantity": "1", "subtotal": "99", "discounts": [], "catalog_price": "99"}], "subtotal": "99"}, "service_fees": {"delivery_cost": "0"}, "discounts_response": {"match_results": [{"results": [{"status": "ok", "discounts": [], "hierarchy_name": "menu_discounts"}, {"status": "ok", "discounts": [], "hierarchy_name": "cart_discounts"}], "subquery_id": "a1664e3e046044baab6d8c0fb2926c1c000100010001"}]}}',
        NULL,
        NULL,
        '2020-09-18 10:56:04.128038+03',
        NULL,
        'available'
    );

UPDATE cart.checkout_data SET promocode_discount = 50, promocode_properties = '{
    "limit": null,
    "source": "eats",
    "discount_type": "fixed",
    "discount_value": "200",
    "tag": "some_tag",
    "series_purpose": "support"
}' WHERE cart_id = 'e6a59113-503c-4d3e-8c59-000000000011';

UPDATE cart.carts SET promocode = 'PROMO1' WHERE cart_id = 'e6a59113-503c-4d3e-8c59-000000000011';

UPDATE cart.checkout_data SET promocode_discount = 50, promocode_properties = '{
    "limit": null,
    "source": "eats",
    "discount_type": "fixed",
    "discount_value": "200",
    "tag": "some_tag",
    "series_purpose": "support"
}' WHERE cart_id = 'e6a59113-503c-4d3e-8c59-000000000021';

UPDATE cart.carts SET promocode = 'PROMO1' WHERE cart_id = 'e6a59113-503c-4d3e-8c59-000000000021';
UPDATE cart.carts SET promocode = 'PROMO1' WHERE cart_id = 'e6a59113-503c-4d3e-8c59-000000000012';

COMMIT TRANSACTION;
