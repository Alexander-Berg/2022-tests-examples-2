--- basic

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000000', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id)
VALUES ('00000000-0000-0000-0000-000000000000', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-exists');


--- wrong user

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000001', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id)
VALUES ('00000000-0000-0000-0000-000000000001', 10, 'eats_user_id', '123-wrong', 'eats:123-wrong', array[]::TEXT[], 'checked_out', '111-wronguser');


--- not available product

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000002', '1', '100', 1, 'RUB');

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000002', '2', '55', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id)
VALUES ('00000000-0000-0000-0000-000000000002', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-notavail');


-- promocode

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000003', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id, promocode)
VALUES ('00000000-0000-0000-0000-000000000003', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-promo', 'LAVKA');


-- delivery_type

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000004', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id, delivery_type)
VALUES ('00000000-0000-0000-0000-000000000004', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-delivery', 'rover');

-- cashback

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000005', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id, cashback_flow)
VALUES ('00000000-0000-0000-0000-000000000005', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-cashback', 'gain');

-- tips

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency)
VALUES ('00000000-0000-0000-0000-000000000006', '1', '100', 1, 'RUB');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id, tips_amount, tips_amount_type)
VALUES ('00000000-0000-0000-0000-000000000006', 10, 'eats_user_id', '123', 'eats:123', array[]::TEXT[], 'checked_out', '111-tips', '49', 'absolute');
