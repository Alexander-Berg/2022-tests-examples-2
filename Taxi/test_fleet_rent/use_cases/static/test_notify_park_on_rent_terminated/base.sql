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
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 terminated_at_tz, termination_reason,
 transfer_order_number)
VALUES ('rent_id', 'idempotency_token',
        'park_id', 1,
        'car', '{"car_id": "car_id"}',
        'park_driver_id',
        'affiliation_id',
        '2020-01-01+00', '2020-01-31+00',
        'free',
        '2020-01-02+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'Accepted by driver',
        '2020-01-02+00', 'Terminated by driver',
        'park_id_1');
INSERT INTO rent.park_comm_sync_rent_termination
    (rent_id, created_at)
VALUES ('rent_id', '2020-01-01');
