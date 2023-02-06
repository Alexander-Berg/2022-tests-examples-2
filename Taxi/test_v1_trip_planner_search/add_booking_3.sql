INSERT INTO state.matching_offers (
    offer_id,
    yandex_uid,
    shuttle_id,
    route_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    passengers_count,
    created_at,
    expires_at
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda25ae', '0123456781', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    booking_id,
    offer_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    status,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda25ae', 'acfff773-398f-4913-b9e9-03bf5eda25ae', '0123456781', 'userid_5', 1, 6, 8, 1, 'driving', 1);

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda25ae', 'confirmed', '123');
