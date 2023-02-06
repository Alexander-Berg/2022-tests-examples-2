INSERT INTO bank_userinfo.sessions (
  id,
  yandex_uid,
  phone_id,
  bank_uid,
  antifraud_info,
  status,
  created_at,
  updated_at,
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
  '2022-02-01T20:28:58.838783+00:00',
  '2022-02-01T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd02',
  NULL,
  NULL,
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{}'::jsonb,
  'invalid_token',
  '2022-02-02T20:28:58.838783+00:00',
  '2022-02-02T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd03',
  NULL,
  NULL,
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{}'::jsonb,
  'invalid_token',
  '2022-02-03T20:28:58.838783+00:00',
  '2022-02-03T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd04',
  NULL,
  'phone_id',
  NULL,
  '{}'::jsonb,
  'invalid_token',
  '2022-02-04T20:28:58.838783+00:00',
  '2022-02-04T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd05',
  'uid',
  NULL,
  NULL,
  '{}'::jsonb,
  'invalid_token',
  '2022-02-05T20:28:58.838783+00:00',
  '2022-02-05T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd06',
  'uid',
  'phone_id',
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{}'::jsonb,
  'ok',
  '2022-02-06T20:28:58.838783+00:00',
  '2022-02-06T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd07',
  'uid',
  'phone_id',
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{}'::jsonb,
  'not_authorized',
  '2022-02-07T20:28:58.838783+00:00',
  '2022-02-08T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bd08',
  'uid',
  'phone_id2',
  'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
  '{}'::jsonb,
  'ok',
  '2022-02-08T20:28:58.838783+00:00',
  '2022-02-08T20:28:58.838783+00:00',
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
);
