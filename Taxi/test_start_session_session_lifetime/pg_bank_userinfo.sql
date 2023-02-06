INSERT INTO bank_userinfo.buids (
  bank_uid,
  yandex_uid,
  phone_id,
  status
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '111111',
  'phone_id_1',
  'FINAL'
);

INSERT INTO bank_userinfo.sessions (
  id,
  yandex_uid,
  phone_id,
  bank_uid,
  antifraud_info,
  status,
  old_session_id,
  app_vars,
  created_at,
  updated_at,
  locale
)
VALUES (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be00',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  '2022-06-04T16:00:00+03:00',
  '2022-06-04T16:00:00+03:00',
  'ru'
);
