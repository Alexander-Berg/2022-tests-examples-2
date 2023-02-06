INSERT INTO eats_cart.carts (id, place_id, place_slug, place_business, eater_id, shipping_type, order_nr, deleted_at, created_at, updated_at)
VALUES 
('00000000000000000000000000000000', '1', '1', 'restaurant', '1', 'delivery', NULL, NULL, '2021-01-10T00:00:00Z', '2021-12-12T01:00:00Z'), -- not deleted
('00000000000000000000000000000001', '1', '1', 'restaurant', '2', 'delivery', NULL, '2021-12-10T01:00:00Z', '2021-01-10T00:00:00Z', '2021-12-10T01:00:00Z'), -- not old enough
('00000000000000000000000000000002', '1', '1', 'restaurant', '3', 'delivery', NULL, NULL, '2021-06-10T00:00:00Z', '2021-06-10T01:00:00Z'), -- to be deleted
('00000000000000000000000000000003', '1', '1', 'restaurant', '4', 'delivery', NULL, '2021-02-10T01:00:00Z', '2021-01-10T00:00:00Z', '2021-10-10T01:00:00Z'); -- to be deleted


INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES 
('1', '00000000000000000000000000000000'), -- unchanged, cart is not deleted
('2', NULL), -- unchanged
('3', '00000000000000000000000000000002'), -- to be purged with the cart
('4', NULL); -- unchanged

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, price, quantity)
VALUES 
(1, '00000000000000000000000000000002', 1, 100, 1), -- to be deleted
(2, '00000000000000000000000000000001', 1, 100, 1); -- unchanged

INSERT INTO eats_cart.cart_item_discounts (id, cart_item_id, promo_id, name, promo_type_id)
VALUES 
(1, 1, '1', 'promo', '102'),
(2, 2, '2', 'promo', '102');
