INSERT INTO state.drivers_workshifts_subscriptions
    (subscription_id, workshift_id, driver_id, subscribed_at, status)
VALUES
    (
        1,
        '427a330d-2506-464a-accf-346b31e288b8',
        ('dbid_0', 'uuid_1')::db.driver_id,
        '2020-06-03T10:15:16+0000',
        'planned'::db.reservation_status
    );

INSERT INTO state.shuttles
    (
        shuttle_id,
        driver_id,
        route_id,
        capacity,
        ticket_length,
        work_mode,
        subscription_id
    )
VALUES
    (
        1,
        ('dbid_0', 'uuid_1')::db.driver_id,
        1,
        16,
        3,
        'shuttle_fix'::db.driver_work_mode,
        1
    );

INSERT INTO state.pauses
    (
        pause_id,
        shuttle_id,
        pause_requested,
        pause_started,
        expected_pause_finish
    )
VALUES
    (
        1,
        1,
        '2020-06-04T11:00:00+0000',
        '2020-06-04T11:02:00+0000',
        '2020-06-04T11:12:00+0000'
    );


UPDATE state.shuttles
SET
    pause_state = 'in_work'::db.pause_state,
    pause_id = 1
WHERE
    shuttle_id = 1;

INSERT INTO state.shuttle_trip_progress
    (shuttle_id, lap, begin_stop_id, next_stop_id, updated_at, advanced_at)
VALUES
    (1, 1, 1, 3, NOW(), NOW());
