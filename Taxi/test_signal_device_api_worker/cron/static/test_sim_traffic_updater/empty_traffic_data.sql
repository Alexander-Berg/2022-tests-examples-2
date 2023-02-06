INSERT INTO signal_device_api.sim_stats (
  msisdn,
  mb_spent_daily,
  day,
  max_session_at
) VALUES
(
    'test',
    1,
    '2021-01-04',
    '2021-01-04 13:39:40'
),
(
    'test2',
    1,
    '2021-01-10',
    '2021-01-10 13:39:40'
),
(
    'test',
    0,
    '2021-01-05',
    '2021-01-05 00:00:00'
),
(
    'test',
    0,
    '2021-01-06',
    '2021-01-06 00:00:00'
);

INSERT INTO signal_device_api.sim_meta(
  imsi,
  msisdn,
  created_at,
  max_session_at,
  last_requested_traffic_datetime
) VALUES
(
  'lol',
  'test',
  '2021-01-01 13:39:41',
  '2021-01-01 13:39:40',
  '2021-01-04 00:00:00'
);
