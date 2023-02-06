ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger;

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
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730001', '0000000001', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-09-14T12:00:00+0000', '2020-09-14T12:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e20002', '0000000002', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-09-14T12:00:00+0000', '2020-09-14T12:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    ticket,
    dropoff_lap,
    created_at,
    cancel_reason,
    finished_at
)
VALUES (
    '0000000001',
    'userid_01',
    2,
    1,
    2,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730001',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730001',
    'transporting',
    '123',
    1,
    '2020-09-4T11:00:00+0000',
    NULL,
    NULL
), (
    '0000000002',
    'userid_02',
    2,
    2,
    3,
    '427a330d-2506-464a-accf-346b31e20002',
    '427a330d-2506-464a-accf-346b31e20002',
    'cancelled',
    '124',
    1,
    '2020-09-14T10:00:00+0000',
    'by_user',
    '2020-09-14T13:00:00+0000'
)
;

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger;

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730001',
    'confirmed',
    '123'
), (
    '427a330d-2506-464a-accf-346b31e20002',
    'confirmed',
    '124'
)
;


INSERT INTO state.pauses (
    pause_id,
    shuttle_id,
    pause_requested,
    expected_pause_start,
    pause_started,
    expected_pause_finish,
    pause_finished
) VALUES (
    1,
    1,
    '2020-09-14T14:05:55+0000',
    NULL,
    NULL,
    NULL,
    NULL
), (
    2,
    2,
    '2020-09-14T14:06:55+0000',
    NULL,
    NULL,
    NULL,
    NULL
);

UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 1
WHERE shuttle_id = 1;


UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 2
WHERE shuttle_id = 2;
