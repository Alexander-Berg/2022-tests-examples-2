INSERT INTO rent.affiliations(
record_id,
park_id,
original_driver_park_id,
original_driver_id,
creator_uid,
created_at_tz,
state)
VALUES
(
'affiliation1',
'park1',
'driverid1',
'parkid1',
'123456',
'2020-01-01:10:00:00+00',
'new'
);

INSERT INTO rent.records(
record_id,
idempotency_token,
affiliation_id,
owner_park_id,
owner_serial_id,
driver_id,
balance_notify_limit,
begins_at_tz,
ends_at_tz,
creator_uid,
created_at_tz,
asset_type,
asset_params,
charging_type,
charging_params,
charging_starts_at_tz,
accepted_at_tz,
rejected_at_tz,
terminated_at_tz,
transfer_order_number)
VALUES
(
'record_id1',
'token1',
'affiliation1',
'park_id1',
1,
'driver_id1',
1000,
'2020-01-01T00:00:00',
NULL,
'uid1',
'2020-01-01+00',
'car',
'{"car_id": "one"}',
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
  "time": "00:00:00"
}',
'2020-01-01T21:00:00',
'2020-01-01+00',
NULL,
NULL,
'park_id1'
),
(
'record_id2',
'token2',
NULL,
'park_id1',
2,
'driver_id2',
1001,
'2020-01-01T00:00:00',
'2020-01-04T00:00:00',
'uid1',
'2020-01-01+00',
'car',
'{"car_id": "one"}',
'daily',
'{
  "daily_price": "500",
  "periodicity": {
    "type": "fraction",
    "params": {
      "numerator": 2,
      "denominator": 2
    }
  },
  "time": "14:00:00"
}',
'2020-01-02:11:00:00',
'2020-01-01+00',
NULL,
NULL,
'park_id1'
);
