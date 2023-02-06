insert into couriers (id, username) values
(1, 'test1'),
(2, 'test2'),
(3, 'test3');

insert into places (id, address_street, brand_id, region_id) values
(1, 'address1', 1, 1),
(2, 'address2', 1, 2),
(3, 'address3', 2, 3);

insert into orders (order_nr, courier_id, place_id, payment_service, courier_assigned_at)
values
('correct order', 1, 2, 'Card Post Payment', now()),
('30 minutes ago', 2, 3, 'Card Post Payment', NOW() - INTERVAL 30 minute),
('another payment type', 3, 1, 'Another type', NOW()),
('11', 1, 1, 'Card Post Payment', now()),
('12', 3, 3, 'Card Post Payment', now()),
('13', 2, 2, 'Card Post Payment', now());
