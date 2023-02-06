INSERT INTO eats_cart.carts (id, place_id, place_slug, place_business, eater_id, shipping_type, order_nr, deleted_at, created_at, updated_at)
VALUES 
('00000000000000000000000000000000', '1', '1', 'restaurant', '1', 'delivery', NULL, NULL, '2021-10-10T00:00:00Z', '2021-10-10T01:00:00Z'), -- cart for delete
('00000000000000000000000000000001', '1', '1', 'restaurant', '2', 'delivery', NULL, NULL, '2021-09-10T00:00:00Z', '2021-09-10T01:00:00Z'), -- too old updated
('00000000000000000000000000000002', '1', '1', 'restaurant', '3', 'delivery', NULL, NULL, '2021-10-10T00:00:00Z', '2021-10-10T04:00:00Z'), -- to soon updated
('00000000000000000000000000000003', '2', '2', 'restaurant', '4', 'delivery', NULL, NULL, '2021-10-10T00:00:00Z', '2021-10-10T01:00:00Z'), -- wrong place_id
('00000000000000000000000000000004', '1', '1', 'restaurant', '5', 'delivery', 'not null', NULL, '2021-10-10T00:00:00Z', '2021-10-10T01:00:00Z'), -- has order
('00000000000000000000000000000005', '1', '1', 'restaurant', '6', 'delivery', NULL, '2021-10-10T01:00:00Z', '2021-10-10T00:00:00Z', '2021-10-10T01:00:00Z'), -- already deleted
('00000000000000000000000000000006', '1', '1', 'restaurant', '1', 'delivery', NULL, NULL, '2021-10-10T00:00:00Z', '2021-10-10T01:01:00Z'), -- cart for delete
('00000000000000000000000000000007', '1', '1', 'restaurant', '7', 'delivery', NULL, NULL, '2021-10-10T00:00:00Z', '2021-10-10T01:01:00Z'); -- cart for delete


INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES 
('1', '00000000000000000000000000000000'), -- cart for delete
('2', '00000000000000000000000000000001'), -- too old created
('3', '00000000000000000000000000000002'), -- to soon updated
('4', '00000000000000000000000000000003'), -- wrong place_id
('5', '00000000000000000000000000000004'); -- has order
