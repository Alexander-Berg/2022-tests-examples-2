INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid1', 'uuid1')::db.driver_id, 1, 16, 3),
    (('dbid2', 'uuid2')::db.driver_id, 1, 16, 3),
    (('dbid3', 'uuid2')::db.driver_id, 1, 16, 3),
    (('dbid4', 'uuid2')::db.driver_id, 1, 16, 3),
    (('dbid5', 'uuid2')::db.driver_id, 1, 16, 3),
    (('dbid6', 'uuid2')::db.driver_id, 1, 16, 3)
;

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at,
    block_reason,
    processed_at
)
VALUES
    (2, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'not_on_route', '2020-09-14T10:15:16+0000'),
    (3, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'not_on_route', '2020-09-14T10:15:16+0000'),
    (4, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'not_on_route', '2020-09-14T10:15:16+0000'),
    (5, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'not_on_route', '2020-09-14T10:15:16+0000'),
    (6, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'not_on_route', '2020-09-14T10:15:17+0000')
;
