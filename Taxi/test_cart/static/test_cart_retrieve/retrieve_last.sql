INSERT INTO cart.carts
(cart_id, created, status, order_id, cart_version, user_type, user_id, session, bound_sessions, updated)
VALUES
('00000000-0000-0000-0000-000000000000', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'editing', NULL, 1, 'eats_user_id', '0', 'eats:0', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP),
('00000000-0000-0000-0000-000000000001', CURRENT_TIMESTAMP - INTERVAL '2 hour', 'checked_out', NULL, 1, 'eats_user_id', '0', 'eats:0', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP);

INSERT INTO cart.carts
(cart_id, created, status, order_id, cart_version, user_type, user_id, session, bound_sessions, updated)
VALUES
('00000000-0000-0000-0000-000000000002', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'editing', NULL, 1, 'eats_user_id', '1', 'eats:1', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP),
('00000000-0000-0000-0000-000000000003', CURRENT_TIMESTAMP - INTERVAL '2 hour', 'checked_out', 'order-id-1', 1, 'eats_user_id', '1', 'eats:1', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP);

INSERT INTO cart.carts
(cart_id, created, status, order_id, cart_version, user_type, user_id, session, bound_sessions, updated)
VALUES
('00000000-0000-0000-0000-000000000004', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'checked_out', 'order-id-2', 1, 'eats_user_id', '2', 'eats:2', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP),
('00000000-0000-0000-0000-000000000005', CURRENT_TIMESTAMP - INTERVAL '2 hour', 'checked_out', null, 1, 'eats_user_id', '2', 'eats:2', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP);
