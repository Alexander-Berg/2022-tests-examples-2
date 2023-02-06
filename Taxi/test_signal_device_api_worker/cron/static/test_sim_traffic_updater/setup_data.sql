INSERT INTO signal_device_api.sim_stats (
  msisdn,
  mb_spent_daily,
  day,
  max_session_at
) VALUES
(
    'test',
    1,
    '2021-01-01',
    '2021-01-01 13:39:40'
),
(
    'test',
    1,
    '2021-02-01',
    '2021-02-01 13:39:40'
),
(
    'kek',
    2,
    '2021-02-01',
    '2021-02-01 20:00:00'
),
(
    'test_empty',
    3210,
    '2021-02-01',
    '2021-02-01 13:39:42'
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
  '2021-01-01 13:39:39',
  '2021-02-01 13:39:40',
  '2021-02-02 00:00:00'
),
(
  'lol2',
  'kek',
  '2021-02-01 13:39:41',
  '2021-02-01 20:00:00',
  '2021-02-01 00:00:00'
),
(
  'lol3',
  'test_empty',
  '2021-02-01 13:39:41',
  '2021-02-01 13:39:42',
  '2021-02-02 00:00:00'
),
(
  'lol4',
  'test_new',
  '2021-02-01 00:00:00',
  '2021-02-01 00:00:00',
  '2021-02-01 00:00:00'
);
