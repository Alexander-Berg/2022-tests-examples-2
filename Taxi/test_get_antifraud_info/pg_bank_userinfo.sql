INSERT INTO bank_userinfo.sessions (
  id,
  status,
  antifraud_info,
  created_at,
  updated_at
)
VALUES (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdf0',
  'no_antifraud_info',
  '{}'::jsonb,
  '2021-10-31T00:01:00+00:00',
  '2021-10-31T00:02:00+00:00'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
  'has_antifraud_info',
  '{"device_id": "device_id",
    "dict": {"key": "value"}}'::jsonb,
  '2021-10-31T00:01:00+00:00',
  '2021-10-31T00:02:00+00:00'
)
