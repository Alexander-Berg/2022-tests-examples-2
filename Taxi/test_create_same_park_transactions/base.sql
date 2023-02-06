INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
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
        'owner_park_id', 1,
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
        'owner_park_id_1'),
       ('record_id2', 'idempotency_token2',
        'owner_park_id', 2,
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
            "type": "constant",
            "params": null
          },
          "time": "03:00:00"
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-02+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        '2020-01-02 01:00+00', 'termination_reason',
        'owner_park_id_2'),
       ('record_id3', 'idempotency_token3',
        'owner_park_id', 3,
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
        'creator_uid', '2020-01-02+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        NULL, NULL,
        'owner_park_id_3')
;

INSERT INTO rent.same_park_transactions_log
(record_id, serial_id, category_id, description, driver_id, park_id,
 event_at_tz, amount)
VALUES ('record_id1', 1, 'partner_service_recurring_payment', '1 (title)', 'driver_id', 'owner_park_id',
        '2020-01-01+00', '100'),
       ('record_id2', 1, 'partner_service_recurring_payment', '2 (title)', 'driver_id', 'owner_park_id',
        '2020-01-01+00', '100')
;
