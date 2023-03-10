INSERT INTO rent.affiliations
(record_id, state,
 park_id, local_driver_id,
 original_driver_park_id, original_driver_id,
 creator_uid, created_at_tz)
VALUES ('affiliation_id', 'new',
        'park_id', 'park_driver_id',
        'driver_park_id', 'driver_id',
        'creator_uid', '2020-01-01+00');
INSERT INTO rent.records
(record_id, idempotency_token, affiliation_id,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type, charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 rejected_at_tz, rejection_reason,
 terminated_at_tz, termination_reason,
 transfer_order_number, use_event_queue,
 start_clid)
VALUES ('rent_id1', 'idempotency_token1',
        'affiliation_id',
        'park_id', 1, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2020-01-01+00', NULL,
        'daily', '{"daily_price": "123", "periodicity": {"type": "constant", "params": null}, "time":"05:00"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_first'),
       ('rent_id2', 'idempotency_token2',
        'affiliation_id',
        'park_id', 2, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2020-01-01+00', NULL,
        'daily', '{"daily_price": "123", "periodicity": {"type": "constant", "params": null}, "time":"05:00"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_first'),
       ('rent_id3', 'idempotency_token3',
        'affiliation_id',
        'park_id', 3, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2020-01-01+00', NULL,
        'active_days', '{"daily_price": "123"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_first'),
       --- new clid
       ('rent_id4', 'idempotency_token4',
        'affiliation_id',
        'park_id', 4, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2020-01-01+00', NULL,
        'daily', '{"daily_price": "123", "periodicity": {"type": "constant", "params": null}, "time":"05:00"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_second'),
       --- internal rent
       ('rent_id5', 'idempotency_token5',
        NULL,
        'park_id', 5, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2020-01-01+00', NULL,
        'daily', '{"daily_price": "123", "periodicity": {"type": "constant", "params": null}, "time":"05:00"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_first'),
       --- OLD
       ('rent_id6', 'idempotency_token6',
        'affiliation_id',
        'park_id', 6, 'car', '{"car_id": "car_id1", "car_copy_id": null}',
        'park_driver_id',
        '2019-12-12+00', '2019-12-12+00',
        'daily', '{"daily_price": "123", "periodicity": {"type": "constant", "params": null}, "time":"05:00"}',
        '2019-12-12+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', NULL,
        NULL, NULL,
        NULL, NULL,
        'park_id', TRUE, 'clid_first');

INSERT INTO rent.event_queue
    (rent_id, event_number, event_at, executed_at)
VALUES ('rent_id1', 1, '2020-01-01+00', '2020-01-01+00'),
       ('rent_id1', 2, '2020-01-02+00', NULL),
       ('rent_id2', 1, '2020-01-01+00', NULL),
       ('rent_id3', 1, '2020-01-02+00', '2020-01-02+00'),
       ('rent_id4', 1, '2020-01-01+00', NULL),
       ('rent_id5', 1, '2020-01-01+00', NULL),
       ('rent_id6', 1, '2020-01-01+00', NULL);

INSERT INTO rent.active_day_start_triggers
(rent_id, event_number,
 park_id, driver_id,
 lower_datetime_bound, upper_datetime_bound, triggered_at)
VALUES ('rent_id3', 1,
        'park_id', 'park_driver_id',
        '2020-01-01+00', '2020-01-02+00', '2020-01-02+00'),
       ('rent_id3', 2,
        'park_id', 'park_driver_id',
        '2020-01-01+00', '2020-01-02+00', NULL);
