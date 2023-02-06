INSERT INTO bank_userinfo.sessions (
  id,
  yandex_uid,
  phone_id,
  bank_uid,
  antifraud_info,
  status,
  old_session_id,
  created_at,
  updated_at,
  authorization_track_id,
  app_vars,
  locale
)
VALUES (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd01',
  NULL,
  NULL,
  NULL,
  '{}'::jsonb,
  'invalid_token',
  NULL,
  '2022-02-01T20:28:58.838783+00:00',
  '2022-02-02T18:28:58.838783+00:00',
  NULL,
  NULL,
  NULL
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd02',
  'uid',
  'phone_id',
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{"device_id": "device_id", "qwe": "asd"}'::jsonb,
  'ok',
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd01',
  '2022-02-02T20:28:58.838783+00:00',
  '2022-02-03T18:28:58.838783+00:00',
  'authorization_track_id',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
);
