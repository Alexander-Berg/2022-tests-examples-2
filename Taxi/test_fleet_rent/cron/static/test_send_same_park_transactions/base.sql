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
VALUES ('a6762855d59b488790ebd8e564b31ddc', 'idempotency_token1',
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
        'owner_park_id_1')
;

INSERT INTO rent.same_park_transactions_log
(record_id, serial_id, category_id, description, driver_id, park_id, event_at_tz, amount, uploaded_at_tz)
VALUES ('a6762855d59b488790ebd8e564b31ddc', 1, 'category', 'title (#1)', 'driver_id', 'owner_park_id', '2020-01-01+00', '100', '2020-01-01+00'),
       ('a6762855d59b488790ebd8e564b31ddc', 2, 'category', 'title (#1)', 'driver_id', 'owner_park_id', '2020-01-02+00', '0', NULL),
       ('a6762855d59b488790ebd8e564b31ddc', 3, 'category', 'title (#1)', 'driver_id', 'owner_park_id', '2020-01-02 12:00+00', '100', NULL),
       ('a6762855d59b488790ebd8e564b31ddc', 4, 'category', 'title (#1)', 'driver_id', 'owner_park_id', '2020-01-03 12:00+00', '100', NULL)
;
