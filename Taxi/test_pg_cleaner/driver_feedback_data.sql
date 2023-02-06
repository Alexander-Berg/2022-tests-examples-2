INSERT INTO state.driver_feedback_data
(
  session_id,
  driver_id_id,
  data,
  created_at,
  mode_id
)
VALUES
(
  1001,
  IdId('uuid', 'dbid777'),
  '{}',
  '2019-09-01T12:00:00',
  1
),
(
  1002,
  IdId('uuid2', 'dbid777'),
  '{}',
  '2019-09-01T11:59:59',
  1
),
(
  1003,
  IdId('driverSS', '1488'),
  '{}',
  '2019-09-01T10:00:00',
  1
);
