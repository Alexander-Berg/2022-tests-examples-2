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
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type, charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz,
 transfer_order_number,
 use_event_queue)
VALUES ('record_id', 'idempotency_token',
        'park_id', 1, 'other', '{"subtype": "misc"}',
        'driver_id',
        'affiliation_id',
        '2020-01-01+00', '2020-01-31+00',
        'active_days', '{"daily_price": "100"}',
        '2020-01-02+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00',
        'park_id_1',
        TRUE);
INSERT INTO rent.active_day_start_triggers
(rent_id, event_number, park_id, driver_id,
 lower_datetime_bound, upper_datetime_bound, triggered_at, order_id)
VALUES ('record_id', 1, 'driver_park_id', 'driver_id',
        '2020-01-02+00', NULL, '2020-01-02 12:00+00', 'order_id'),
       ('record_id', 2, 'driver_park_id', 'driver_id',
        '2020-01-03+00', NULL, NULL, NULL);
INSERT INTO rent.event_queue
    (rent_id, event_number, event_at, executed_at)
VALUES ('record_id', 1, '2020-01-02 12:00+00', '2020-01-02 13:00+00');

INSERT INTO rent.rent_history(rent_id, version,
                              modification_source,
                              owner_park_id,
                              owner_serial_id,
                              asset_type,
                              asset_params,
                              driver_id,
                              affiliation_id,
                              begins_at, ends_at,
                              charging_type, charging_params,
                              charging_starts_at,
                              creator_uid, created_at,
                              modified_at,
                              accepted_at,
                              transfer_order_number,
                              use_event_queue,
                              use_arbitrary_entries)
VALUES ('record_id', 1,
        '{"kind":"dispatcher", "uid": "user_uid"}'::JSONB,
        'park_id', 1, 'other', '{"subtype": "misc"}',
        'driver_id',
        'affiliation_id',
        '2020-01-01+00', '2020-01-31+00',
        'active_days', '{"daily_price": "100"}',
        '2020-01-02+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00',
        '2020-01-01+00',
        'park_id_1',
        TRUE, FALSE);
