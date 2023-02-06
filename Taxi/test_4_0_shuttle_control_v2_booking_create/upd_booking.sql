ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    locale,
    created_at,
    status,
    ticket,
    offer_id,
    dropoff_lap
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0123456780',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '123',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    1
);

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;
