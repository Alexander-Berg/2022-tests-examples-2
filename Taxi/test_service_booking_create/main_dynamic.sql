INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.643148,55.734349)),
    (3, point(37.642874,55.734083)),
    (4, point(37.642234,55.733778)),
    (5, point(37.640079,55.736952)),
    (6, point(37.641866, 55.737599)),
    (7, point(37.642345, 55.736403));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 2, 'stop2', 'stop__2'),
    (3, 3, 'stop3', 'stop__3'),
    (4, 4, 'stop4', NULL),
    (5, 5, 'stop5', NULL),
    (6, 6, 'stop6', NULL),
    (7, 7, 'stop7', NULL);

INSERT INTO config.routes (
    route_id, name, is_dynamic
)
VALUES
    (1, 'route1', TRUE);

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3),
  (1, 4, NULL),
  (1, 5, 4),
  (1, 6, NULL),
  (1, 7, 5);

INSERT INTO state.route_views (
    route_id, current_view, traversal_plan
)
VALUES
    (1, ARRAY[1, 3, 7],
     ROW(ARRAY[
         (1, NULL, NULL)::db.traversal_plan_point,
         (3, 'acfff773-398f-4913-b9e9-03bf5eda22ac', TRUE)::db.traversal_plan_point,
         (7, 'acfff773-398f-4913-b9e9-03bf5eda22ac', FALSE)::db.traversal_plan_point])::db.traversal_plan)
;

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length, view_id
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 4, 3, 1);

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
    created_at,
    expires_at,
    pickup_timestamp,
    dropoff_timestamp,
    suggested_route_view,
    suggested_traversal_plan
)
VALUES
  ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 1, 1, point(30, 60), point(31, 61), 3, 1, 7, 1, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '2020-01-17T18:00:00+0000', '2020-01-17T18:00:00+0000', NULL, NULL),
  ('acfff773-398f-4913-b9e9-03bf5eda22ad', '0123456789', 1, 1, point(37.643148, 55.734349), point(37.641866, 55.737599), 2, 1, 6, 1, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '2020-01-17T18:00:00+0000', '2020-01-17T18:00:00+0000',
   ARRAY[1, 2, 3, 6, 5, 7],
   ROW(ARRAY[
       (1, NULL, NULL)::db.traversal_plan_point,
       (2, NULL, NULL)::db.traversal_plan_point,
       (3, 'acfff773-398f-4913-b9e9-03bf5eda22ac', TRUE)::db.traversal_plan_point,
       (6, NULL, NULL)::db.traversal_plan_point,
       (5, NULL, NULL)::db.traversal_plan_point,
       (7, 'acfff773-398f-4913-b9e9-03bf5eda22ac', FALSE)::db.traversal_plan_point])::db.traversal_plan);

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    offer_id,
    dropoff_lap,
    status
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 'userid_1', 1, 3, 7, 1, 'acfff773-398f-4913-b9e9-03bf5eda22ac', 1, 'driving');

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '101', 'issued');

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    end_lap,
    end_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 0, 1, 1, NULL, NULL, NOW(), NOW()); -- shuttle starting its ride
