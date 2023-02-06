INSERT INTO terminal_tokens (id, place_id)
VALUES
(1, '1'),
(2, '2');

INSERT INTO places (place_id, balance_client_id, name, region_id, address_city, address_short, address_comment, brand_id, brand_name, location)
VALUES
('1', '1', '', '', '', '', '', '', '', POINT(0, 0)),
('2', '2', '', '', '', '', '', '', '', POINT(0, 0));
