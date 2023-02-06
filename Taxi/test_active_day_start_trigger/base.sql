INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz,
 transfer_order_number)
VALUES ('record_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'active_days',
 '{"daily_price": "123"}',
 '2020-01-02+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');

INSERT INTO rent.active_day_start_triggers
(rent_id, event_number,
 park_id, driver_id,
 lower_datetime_bound, upper_datetime_bound)
VALUES ('record_id', 1,
 'park_id', 'driver_id',
 '2020-01-01+00', '2020-01-02+00');
