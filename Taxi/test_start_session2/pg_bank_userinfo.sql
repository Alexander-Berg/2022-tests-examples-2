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
),(
  '48c3d180-e14e-4e64-8de3-407b0b3b735a',
  '111110',
  'phone_id_2',
  'FINAL'
),(
  'ff89568b-c667-4bb0-9f92-dbaac0672728',
  '111112',
  'phone_id_3',
  'FINAL'
),(
  'e0cfac83-f7a2-452e-9b8e-bfc7a3aef579',
  '111113',
  'phone_id_4',
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
  authorization_track_id,
  app_vars,
  locale
)
VALUES (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be00',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{"device_id": "12345", "client_ip": "", "additionalProp1": {"test_add_prop": "54321"}}',
  'ok',
  NULL,
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
),(
  '024e7db5-9bd6-4f45-a1cd-2a442e15be01',
  '111112',
  'phone_id_3',
  'ff89568b-c667-4bb0-9f92-dbaac0672728',
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'not_authorized',
  NULL,
  'default_track_id',
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
),(
  '024e7db5-9bd6-4f45-a1cd-2a442e15be02',
  '111113',
  'phone_id_4',
  'e0cfac83-f7a2-452e-9b8e-bfc7a3aef579',
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'not_authorized',
  NULL,
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
);
