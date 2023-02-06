INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode
)
VALUES
       (
            2,
            ('111', '888')::db.driver_id,
            1,
            16,
            3,
            'shuttle_fix'
       ),
       (
           3,
           ('111', '999')::db.driver_id,
           1,
           16,
           3,
           'shuttle_fix'
       );

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    begin_stop_id,
    lap,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES (2,
        1,
        1,
        2,
        NOW(),
        NOW()
        ),
       (
        3,
        1,
        1,
        2,
        NOW(),
        NOW()
       );
