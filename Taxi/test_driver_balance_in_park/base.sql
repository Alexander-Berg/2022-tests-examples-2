INSERT INTO rent.affiliations
(record_id, state,
 park_id, local_driver_id,
 original_driver_park_id, original_driver_id,
 creator_uid, created_at_tz)
VALUES
('affiliation_id', 'active',
 'park_id', 'local_driver_id',
 'driver_park_id', 'driver_id',
 'creator_uid', '2020-01-01+00');

INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id, affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz,
 transfer_order_number)
VALUES ('record_id1', 'idempotency_token1',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id', 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'free',
 '2020-01-02+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1'),
 ('record_id2', 'idempotency_token2',
 'park_id', 2, 'other', '{"subtype": "misc"}',
 'driver_id', 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'free',
 '2020-01-02+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_2');
