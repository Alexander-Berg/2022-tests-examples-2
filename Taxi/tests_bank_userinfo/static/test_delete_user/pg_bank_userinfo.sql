INSERT INTO bank_userinfo.phones (
  phone_id,
  phone
)
VALUES (
  '9d451b58-4d90-4336-9750-8ae222bc36cf',
  '+79111111112'
);

INSERT INTO bank_userinfo.buids (
  bank_uid,
  yandex_uid,
  phone_id,
  status
)
VALUES (
  'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855',
  '111111',
  '9d451b58-4d90-4336-9750-8ae222bc36cf',
  'NEW'
), (
  'eec3d97f-a6d0-4047-b2a0-cdb64a5fc866',
  NULL,
  NULL,
  'FINAL'
), (
  'eec3d97f-a6d0-4047-b2a0-cdb64a5fc877',
  NULL,
  NULL,
  'NEW'
)
