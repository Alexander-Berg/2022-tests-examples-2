INSERT INTO bank_userinfo.buids (
  bank_uid,
  yandex_uid,
  phone_id,
  status
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
  'FINAL'
);

INSERT INTO bank_userinfo.sessions (
  id,
  yandex_uid,
  phone_id,
  bank_uid,
  status,
  antifraud_info,
  created_at,
  updated_at,
  app_vars,
  locale
)
VALUES
 (
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdc1',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
   '7948e3a9-623c-4524-a390-9e4264d27a77',
   'first_session',
   '{"device_id": "device_id",
     "dict": {"key": "value"}}'::jsonb,
   '2021-10-31T00:01:00+00:00',
   '2021-10-31T00:02:00+00:00',
   NULL,
   NULL
 ), (
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
   '7948e3a9-623c-4524-a390-9e4264d27a77',
   'second_session',
   '{"device_id": "device_id",
     "dict": {"key": "value"}}'::jsonb,
   '2021-10-31T00:02:00+00:00',
   '2021-10-31T00:05:00+00:00',
   NULL,
   NULL
 ), (
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdc3',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
   '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
   '7948e3a9-623c-4524-a390-9e4264d27a77',
   'latest_session',
   '{"device_id": "device_id",
     "dict": {"key": "value"}}'::jsonb,
   '2021-10-31T00:03:00+00:00',
   '2021-10-31T00:07:00+00:00',
   NULL,
   NULL
 )

