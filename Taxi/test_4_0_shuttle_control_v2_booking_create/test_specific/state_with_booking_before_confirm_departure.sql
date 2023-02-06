INSERT INTO state.route_views
    (route_id, current_view, traversal_plan)
VALUES
    (
        1,
        ARRAY[3, 4, 1],
        ROW(
            ARRAY[
                (3, 'acfff773-398f-4913-b9e9-03bf5eda22ac', TRUE)::db.traversal_plan_point,
                (4, 'acfff773-398f-4913-b9e9-03bf5eda22ac', FALSE)::db.traversal_plan_point,
                (1, NULL, NULL)::db.traversal_plan_point
            ]
        )::db.traversal_plan
    );

INSERT INTO state.shuttles
    (shuttle_id, driver_id, route_id, is_fake, capacity, ticket_length, view_id)
VALUES
    (1, ('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 4, 3, 1);

INSERT INTO state.matching_offers
    (
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
    (
        'acfff773-398f-4913-b9e9-03bf5eda22ac',
        '0001',
        1,
        1,
        point(37.642874,55.734083),
        point(37.642234,55.733778),
        3,
        1,
        4,
        1,
        (10, 'RUB')::db.trip_price,
        '2020-01-17T18:00:00+0000',
        '2020-01-17T18:18:00+0000',
        '2020-01-17T18:00:00+0000',
        '2020-01-17T18:00:00+0000',
        ARRAY[3, 4, 1],
        ROW(
            ARRAY[
                (3, NULL, NULL)::db.traversal_plan_point,
                (4, NULL, NULL)::db.traversal_plan_point,
                (1, NULL, NULL)::db.traversal_plan_point
            ]
        )::db.traversal_plan
    ),
    (
        'acfff773-398f-4913-b9e9-03bf5eda22ad',
        '0002',
        1,
        1,
        point(37.642874,55.734083),
        point(37.642234,55.733778),
        3,
        1,
        4,
        1,
        (10, 'RUB')::db.trip_price,
        '2020-01-17T18:00:00+0000',
        '2020-01-17T18:18:00+0000',
        '2020-01-17T18:00:00+0000',
        '2020-01-17T18:00:00+0000',
        ARRAY[3, 4, 1],
        ROW(
            ARRAY[
                (3, 'acfff773-398f-4913-b9e9-03bf5eda22ac', TRUE)::db.traversal_plan_point,
                (4, 'acfff773-398f-4913-b9e9-03bf5eda22ac', FALSE)::db.traversal_plan_point,
                (1, NULL, NULL)::db.traversal_plan_point
            ]
        )::db.traversal_plan
    );

INSERT INTO state.passengers
    (
        booking_id,
        offer_id,
        yandex_uid,
        user_id,
        shuttle_id,
        stop_id,
        dropoff_stop_id,
        shuttle_lap,
        dropoff_lap,
        status
    )
VALUES
    (
        'acfff773-398f-4913-b9e9-03bf5eda22ac',
        'acfff773-398f-4913-b9e9-03bf5eda22ac',
        '0001',
        'userid_1',
        1,
        3,
        4,
        1,
        1,
        'transporting'::db.booking_status
    );

INSERT INTO state.booking_tickets
    (booking_id, code, status)
VALUES
    (
        'acfff773-398f-4913-b9e9-03bf5eda22ac',
        '101',
        'confirmed'::db.ticket_status
    );

INSERT INTO state.shuttle_trip_progress
    (shuttle_id, lap, begin_stop_id, next_stop_id, updated_at, advanced_at)
VALUES
    (1, 0, 1, 3, NOW(), NOW());
