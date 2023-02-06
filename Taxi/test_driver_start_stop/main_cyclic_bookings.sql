INSERT INTO state.matching_offers(
    offer_id,
    shuttle_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    expires_at,
    created_at,
    route_id
)
VALUES
('acfff773-398f-4913-b9e9-03bf5eda22ac', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('acfff773-398f-4913-b9e9-03bf5eda22ad', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    status,
    offer_id,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 'userid_1', 1, 5, 1, 1, 'created', 'acfff773-398f-4913-b9e9-03bf5eda22ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda22ad', '012345679', 'userid_2', 1, 5, 3, 1, 'driving', 'acfff773-398f-4913-b9e9-03bf5eda22ad', 2);

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
) VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '0101', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '0102', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda22ad', '0202', 'issued');
