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
),  (
  '0543be85-4adc-4b79-88c5-42ea9e7516c1',
  '111114',
  'phone_id_4',
  'PHONE_CONFIRMED'
),  (
  '96b35805-ff7b-4bdf-a68d-813756a3ba5c',
  '111115',
  NULL,
  'NEW'
),  (
  '0d1f48c9-b5fb-4732-bbb7-09b7dc9e6dfb',
  '111116',
  NULL,
  'FINAL'
),  (
  'd524e191-7af7-4159-b58a-043627dc5228',
  '111117',
  'phone_id_7',
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
  locale
)
VALUES (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdf9',
  NULL,
  NULL,
  NULL,
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'invalid_token',
  NULL,
  NULL,
  NULL
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfa',
  NULL,
  NULL,
  NULL,
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfb',
  '111111',
  NULL,
  NULL,
  '{}',
  'invalid_token',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfc',
  '111111',
  NULL,
  NULL,
  '{}',
  'not_registered',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfd',
  NULL,
  NULL,
  NULL,
  '{}',
  'invalid_token',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfe',
  '111111',
  NULL,
  NULL,
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdff',
  '111111',
  'phone_id_1',
  NULL,
  '{}',
  'not_registered',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be00',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be01',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be02',
  NULL,
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be03',
  '111112',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be04',
  '111111',
  'phone_id_2',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be05',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a78',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be06',
  '111111',
  'phone_id_1',
  NULL,
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be07',
  '111111',
  'phone_id_2',
  NULL,
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be08',
  '111112',
  'phone_id_2',
  NULL,
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be09',
  '111111',
  'phone_id_1',
  NULL,
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0a',
  '111111',
  'phone_id_2',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0a',
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0b',
  '111111',
  'phone_id_2',
  NULL,
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0c',
  NULL,
  'phone_id_2',
  NULL,
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0d',
  '111111',
  NULL,
  NULL,
  '{}',
  'phone_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0e',
  '111112',
  'phone_id_1',
  NULL,
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0f',
  '111111',
  'phone_id_1',
  NULL,
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be10',
  '111112',
  'phone_id_2',
  NULL,
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be11',
  '111112',
  'phone_id_1',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be11',
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be12',
  '111112',
  'phone_id_1',
  NULL,
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be13',
  NULL,
  'phone_id_1',
  NULL,
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be14',
  '111112',
  NULL,
  NULL,
  '{}',
  'account_recovery_required',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '111112',
  'phone_id_2',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be16',
  '111112',
  'phone_id_2',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'yet_another_not_real_status',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be17',
  '111112',
  'phone_id_2',
  NULL,
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be18',
  '111113',
  'phone_id_2',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be19',
  NULL,
  'phone_id_2',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be1a',
  '111112',
  'phone_id_3',
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be1b',
  '111112',
  NULL,
  '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
  '{}',
  'ok',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '6723253c-8df5-4bee-bc44-c3806d6860f6',
  '111118',
  NULL,
  NULL,
  '{"device_id": "e17d59f4f273e5fefcc6b8435909ff46", "client_ip": ""}',
  'not_registered',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be1c',
  '111117',
  'phone_id_7',
  'd524e191-7af7-4159-b58a-043627dc5228',
  '{}',
  'not_authorized',
  NULL,
  'app_name=sdk_example,X-Platform=fcm',
  'ru'
)
