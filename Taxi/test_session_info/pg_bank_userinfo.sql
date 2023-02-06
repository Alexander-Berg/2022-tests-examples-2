INSERT INTO bank_userinfo.sessions (
  id,
  yandex_uid,
  phone_id,
  bank_uid,
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
  'invalid_token',
  NULL,
  'X-Platform=fcm, app_name=sdk_example',
  'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdfc',
  '111111',
  NULL,
  NULL,
  'not_registered',
  NULL,
   'X-Platform=fcm, app_name=sdk_example',
   'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be00',
  '111111',
  'phone_id_1',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  'ok',
  NULL,
   'X-Platform=fcm, app_name=sdk_example',
   'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be07',
  '111111',
  'phone_id_2',
  NULL,
  'phone_recovery_required',
  NULL,
   'X-Platform=fcm, app_name=sdk_example',
   'ru'
), (
  '024e7db5-9bd6-4f45-a1cd-2a442e15be0e',
  '111112',
  'phone_id_1',
  NULL,
  'account_recovery_required',
  NULL,
   'X-Platform=fcm, app_name=sdk_example',
   'ru'
)
