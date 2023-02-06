
INSERT INTO eats_cart.carts (id, place_id, place_slug, place_business, eater_id, shipping_type, order_nr, deleted_at, created_at, updated_at, total, promo_subtotal)
VALUES 
('00000000000000000000000000000001', '1', '1', 'restaurant', '2', 'delivery', NULL, NULL, '2022-01-01T00:00:00Z', '2022-01-01T01:00:00Z', 200, 190), 
('00000000000000000000000000000002', '2', '2', 'shop', '3', 'delivery', NULL, NULL, '2022-01-01T00:00:00Z', '2022-01-01T04:00:00Z', 220, 200),
('00000000000000000000000000000003', '2', '2', 'shop', '3', 'delivery', NULL, '2022-01-01T04:00:00Z', '2022-01-01T00:00:00Z', '2022-01-01T04:00:00Z', 220, 200);

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, price, quantity)
VALUES 
(1, '00000000000000000000000000000002', 1, 100, 1),
(2, '00000000000000000000000000000001', 1, 100, 2),
(3, '00000000000000000000000000000002', 2, 60, 2),
(4, '00000000000000000000000000000003', 2, 60, 2);
