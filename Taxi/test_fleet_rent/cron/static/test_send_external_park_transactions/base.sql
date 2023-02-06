INSERT INTO rent.affiliations
(record_id, state,
 park_id, local_driver_id,
 original_driver_park_id, original_driver_id,
 creator_uid, created_at_tz)
VALUES ('affiliation_id', 'new',
        'park_id', 'driver_id',
        'original_driver_park_id', 'original_driver_id',
        'creator_uid', '2020-01-01+00')
;

INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 affiliation_id,
 asset_type,
 asset_params,
 title,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 rejected_at_tz, rejection_reason,
 terminated_at_tz, termination_reason,
 transfer_order_number)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'affiliation_id',
        'other',
        '{
          "subtype": "misc"
        }',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'daily',
        '{
          "daily_price": "100",
          "periodicity": {
            "type": "fraction",
            "params": {
              "numerator": 1,
              "denominator": 1
            }
          },
          "time": "03:00:00"
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        NULL, NULL,
        '1'),
       ('record_id2', 'idempotency_token2',
        'park_id', 2,
        'affiliation_id',
        'other',
        '{
          "subtype": "misc"
        }',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'daily',
        '{
          "daily_price": "100",
          "periodicity": {
            "type": "fraction",
            "params": {
              "numerator": 1,
              "denominator": 1
            }
          },
          "time": "03:00:00"
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        NULL, NULL,
        'park_id_2')
;

INSERT INTO rent.external_park_transactions_log
(record_id, serial_id, record_serial_id,
 park_id, local_driver_id,
 external_driver_id, external_driver_park_id,
 amount, scheduled_at_tz, uploaded_at_tz)
VALUES ('record_id1', 1, 1,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '100', '2020-01-01+00', '2020-01-01+00'),
       ('record_id1', 2, 1,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '0', '2020-01-02+00', NULL),
       ('record_id1', 3, 1,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '100', '2020-01-03+00', NULL),
       ('record_id2', 1, 2,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '100', '2020-01-01+00', '2020-01-01+00'),
       ('record_id2', 2, 2,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '0', '2020-01-02+00', NULL),
       ('record_id2', 3, 2,
        'park_id', 'driver_id',
        'original_driver_id', 'original_driver_park_id',
        '100', '2020-01-03+00', NULL)
;
