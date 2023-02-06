
insert into brands (name)
values ('1'), ('2'), ('3'),('4'),('5'),('6');

insert into regions (name)
values ('Москва'), ('Железнодорожный'), ('3');

insert into orders
(
    order_nr,
    status,
    is_asap,
    arrived_to_customer_at,
    call_center_confirmed_at,
    place_id,
    place_confirmed_at
)
values
('1', 1, 1, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 1, '2021-02-01 02:30:00'),
('1', 2, 1, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 2, '2021-02-01 02:30:00'),
('1', 7, 0, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 2, '2021-02-01 02:30:00'),
('1', 0, 0, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 2, '2021-02-01 02:30:00'),
('1', 5, 1, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 1, '2021-02-01 02:30:00'),
('1', 8, 0, '2021-02-01 02:00:00', '2021-02-01 02:15:00', 1, '2021-02-01 02:30:00');

insert into order_cancels (order_id)
values (7);

insert into order_cancel_tasks(order_cancel_id, reaction_id)
values (1, 1);
