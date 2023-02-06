INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id)
VALUES ('00000000-0000-0000-0000-000000000000', 1, 'eats_user_id', '0', 'eats:0', array['taxi:1234']::TEXT[], 'checked_out', null);

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, status, order_id)
VALUES ('00000000-0000-0000-0000-000000000001', 1, 'eats_user_id', '1', 'eats:1', array['taxi:1234']::TEXT[], 'checked_out', '777');
